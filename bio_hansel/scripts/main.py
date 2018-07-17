import argparse
import logging
import os
import sys

from find_cluster import find_clusters
from fisher_test import fisher_test
from write_sequence import write_sequences, get_sequences
from read_vcf import read_vcf

SCRIPT_NAME = 'schema_creation'
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'


def init_console_logger(logging_verbosity=3):
    logging_levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    if logging_verbosity > (len(logging_levels) - 1):
        logging_verbosity = 3
    lvl = logging_levels[logging_verbosity]

    logging.basicConfig(format=LOG_FORMAT, level=lvl)


def init_parser():
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        '-i',
        '--input-vcf',
        required=True,
        help=
        'vcf file containing the list of SNVs that are related to the genomes')

    parser.add_argument(
        '-g',
        '--reference-genome-file',
        required=True,
        help='Path to reference genome name, can be .gb or .gbk format')
    parser.add_argument(
        '-o',
        '--output-folder-name',
        required=True,
        help=
        'Output file name for the genomes, default folder name is /usr/home/genomes'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help=
        'Logging verbosity level (-v == show warnings; -vvv == show debug info)'
    )

    parser.add_argument(
        '-n',
        '--schema-name',
        help=
        'A unique name for the schema file that is generated, the default is just'
        ' {bio_hansel-schema-reference_genome_name}-{schema_version}')

    parser.add_argument(
        '-m',
        '--schema-version',
        help='An optional version number for the schema file that is generated'
    )

    parser.add_argument(
        '-t',
        '--minimum-threshold',
        required=True,
        type=float,
        help=
        'Minimum threshold to be tested using the hierarchical clustering scheme'
    )

    parser.add_argument(
        '-u',
        '--maximum-threshold',
        required=True,
        type=float,
        help=
        'Maximum threshold to be tested using the hierarchical clustering scheme'
    )

    parser.add_argument(
        '-s',
        '--padding-sequence-length',
        required=True,
        type=int,
        help=
        'Length of additional sequences to be added to the beginning and end of the selected SNV'
    )

    return parser


def main():
    parser = init_parser()
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()
    args = parser.parse_args()
    output_directory = args.output_folder_name
    min_threshold = args.minimum_threshold
    max_threshold = args.maximum_threshold

    if (min_threshold >= max_threshold):
        logging.error("max_threshold has to be bigger than min_threshold")
    init_console_logger(3)
    vcf_file = args.input_vcf
    reference_genome_path = args.reference_genome_file
    sequence_length = args.padding_sequence_length

    reference_genome_name = reference_genome_path.split("/")[-1]
    reference_genome_name = reference_genome_name.split(".")[-2]
    logging.info('using genbank file from %s', reference_genome_path)

    if args.schema_version is not None:
        schema_version = args.schema_version
    else:
        schema_version = "0.1.0"

    if args.schema_name is not None:
        schema_name = args.schema_name - {schema_version}
    else:
        schema_name = f"bio_hansel-schema-{reference_genome_name}-{schema_version}"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    data_frame = read_vcf(vcf_file)
    groups_dict = find_clusters(data_frame, min_threshold, max_threshold)
    results_dict = fisher_test(data_frame, groups_dict)
    updated_results_dict = get_sequences(results_dict, sequence_length)
    write_sequences(output_directory, updated_results_dict, schema_name)


if __name__ == '__main__':
    main()

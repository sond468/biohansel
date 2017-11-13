from typing import List, Callable, Tuple, Optional

from pandas import DataFrame

from bio_hansel.quality_check.qc_utils import get_hit_and_miss_tiles
from bio_hansel.quality_check.quality_check_functions import check_intermediate_subtype
from bio_hansel.quality_check.const import PASS_MESSAGE, FAIL_MESSAGE, WARNING_MESSAGE
from bio_hansel.subtype import Subtype


QC_FUNCS: List[Callable[[Subtype], Tuple[str, str]]] = \
[

]


def perform_quality_check(st: Subtype, df: DataFrame):
    overall_qc_status = 'PASS'
    messages = []

    check_intermediate_subtype(st, df)
    # This needs to be refactored.
    '''
    if does_subtype_result_exist(st) is False:
        st.qc_status = 'FAIL'
        st.qc_message = 'FAIL: No matching tiles exist, quality checking was not run.'
        return None
'''
    for func in QC_FUNCS:
        # Calls run_method to check that the qc function takes a Subtype, returns Tuple[Optional[str], Optional[str]]
        status, message = run_method(func, st)
        if status is None:
            # If quality check function passes, move on to the next.
            continue
        messages.append('{}: {}'.format(status, message))
        if status is FAIL_MESSAGE:
            overall_qc_status = 'FAIL'
        elif overall_qc_status != 'FAIL' and status == WARNING_MESSAGE:
            overall_qc_status = 'WARNING'

    st.qc_status = overall_qc_status
    st.qc_message = ' | '.join(messages)


# Helper method used to ensure function being called is of the right type.
def run_method(func: Callable[[Subtype], Tuple[str, str]], st: Subtype) -> Tuple[Optional[str], Optional[str]]:
    return func(st)

from ccdxt.base.utils.type import * 
from ccdxt.base.utils.hexadecimal import * 

def is_wallet_address(value) -> bool:
    """
    Checks if value is T_ADDR_EOA type.
    T_ADDR_EOA is data type which is 40-digit hexadecimal string prefixed with `hx`.

    :param value: wallet address
    """
    return is_str(value) and value.islower() and is_hx_prefixed(value) and len(remove_hx_prefix(value)) == 40


def is_score_address(value) -> bool:
    """
    Checks if value is T_ADDR_SCORE type.
    T_ADDR_SCORE is data type which is 40-digit hexadecimal string prefixed with `cx`.

    :param value: SCORE address
    """
    return is_str(value) and value.islower() and is_cx_prefixed(value) and len(remove_cx_prefix(value)) == 40
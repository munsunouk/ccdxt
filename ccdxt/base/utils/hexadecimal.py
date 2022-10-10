from ccdxt.base.utils.type import is_str
from ccdxt.base.utils.errors import DataTypeError

def is_hx_prefixed(value: str) -> bool:
    """Used for checking an address of a wallet."""
    if not is_str(value):
        raise DataTypeError("Value type must be str. Got: {0}.".format(repr(value)))
    return value.startswith('hx')

def remove_hx_prefix(value: str) -> str:
    if is_hx_prefixed(value):
        return value[2:]
    return value

def is_cx_prefixed(value: str) -> bool:
    """Used for checking an address of Contract."""
    if not is_str(value):
        raise DataTypeError("Value type must be str. Got: {0}.".format(repr(value)))
    return value.startswith("cx")

def remove_cx_prefix(value: str) -> str:
    if is_cx_prefixed(value):
        return value[2:]
    return value
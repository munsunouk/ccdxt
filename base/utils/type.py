from numbers import Number
from typing import Mapping

bytes_types = (bytes, bytearray)
integer_types = (int,)
str_types = (str,)
string_types = (bytes, str, bytearray)


def is_integer(value) -> bool:
    return isinstance(value, integer_types) and not isinstance(value, bool)


def is_bytes(value) -> bool:
    return isinstance(value, bytes_types)


def is_str(value) -> bool:
    return isinstance(value, str_types)


def is_boolean(value) -> bool:
    return isinstance(value, bool)


def is_dict(obj) -> bool:
    return isinstance(obj, Mapping)


def is_list(obj) -> bool:
    return isinstance(obj, list)


def is_tuple(obj) -> bool:
    return isinstance(obj, tuple)


def is_null(obj) -> bool:
    return obj is None


def is_number(obj) -> bool:
    return isinstance(obj, Number)
from decimal import Decimal

class BigNumber(object):
    """BigNumber is used for creating etheruem friendly numbers."""

    def __init__(self, value : float or int, exp : int=18) :
        self.value = value
        self.exp = exp

    def __eq__(self, other) :
        if isinstance(other, BigNumber) :
            return self.value == other.value and self.exp == other.exp
        return self.value == other

    def __gt__(self, other) :
        if isinstance(other, BigNumber) :
            return self.value > other.value
        return self.value > other

    def __truediv__(self,other) :
        return self.to_number() / other.to_number()

    def from_value(self) -> int :
        return int(round(self.value * 10 ** self.exp))

    def to_value(self)-> Decimal :
        return Decimal(self.value) / Decimal(10 ** self.exp)
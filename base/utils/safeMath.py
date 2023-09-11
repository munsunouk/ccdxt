from mars.base.utils.errors import \
    AdditionOverFlowError, \
    SubtractionOverFlowError, \
    MultiplicationOverFlowError, \
    DivisionByZero, \
    ModuloByZeroError, \
    NegativeNumbers
from typing import Union
from decimal import Decimal
import math
import logging

from typing import Any, Generator, List, Sequence, Tuple, Union

class SafeMath:
	'''
	Wrapper over arithmetic operations in python with added overflow checks.
	'''
 
	def __init__(self) -> None:
		# Source: https://github.com/Uniswap/v3-core/blob/v1.0.0/contracts/libraries/TickMath.sol#L8-L11
		self.min_tick = -887272
		self.max_tick = -self.min_tick

		# Source: https://github.com/Uniswap/v3-core/blob/v1.0.0/contracts/UniswapV3Factory.sol#L26-L31
		self._tick_spacing = {100:1, 500: 10, 3_000: 60, 10_000: 200}
    
	def truncate(number,digits=0):
     
		try :
     
			if digits == 0 :
				return math.trunc(number)
			nbDecimals = len(str(number).split('.')[1])
			if nbDecimals <= digits:
				return number
			stepper = 10.0 ** digits
			return math.trunc(stepper * number) / stepper

		except :
      
			logging.info(number)

	def add(a: int, b: int) -> int:
		'''
		Returns the sum of two unsigned integers after overflow check.
		Counterpart to default `+` operator in python.
		
		:param a: The first number. 
		:param b: The second number.
		:return Sum of `a` and `b`
		Raise
		NegativeNumbers
			If `a` or `b` is negative.
		AdditionOverFlowError
			In case of overflow.
			It occurs for extremely large values.
		>>> add(2,3)
		5
		'''
		if (a < 0 or b < 0):
			raise NegativeNumbers("Numbers cannot be negative")
			return
		c = a + b
		if (c < a or c < b):
			raise AdditionOverFlowError("Addition overflow occured.")
			return
		else:
			return c

	def sub(a: int, b: int) -> int:
		'''
		Returns the difference of two unsigned integers, reverting when the result is neagtive.
		Counterpart to default `-` operator in python.
		
		:param a: The first number. 
		:param b: The second number.
		:return Difference of `a` and `b` if `a` > `b`
		Raise
		NegativeNumbers
			If `a` or `b` is negative.
		SubtractionOverFlowError
			If `a`+`b` greater than `a`.
		>>> sub(3,2)
		1
		>>> sub(3,4)
		SubtractionOverFlowError: First argument must be greater than the second.
		'''
		if (a < 0 or b < 0):
			raise NegativeNumbers("Numbers cannot be negative.")
		if b > a:
			raise SubtractionOverFlowError("First argument must be greater than the second.")
		else:
			c = a - b
			return c

	def mul(a: int, b: int) -> int:
		'''
		Returns the product of two unsigned integers, reverting in case of overflow.
		Counterpart to default `*` operator in python.
		
		:param a: The first number, multiplicand. 
		:param b: The second number, multiplier.
		:return Product of `a` and `b` after checks.
		Raise
		NegativeNumbers
			If `a` or `b` is negative.
		MultiplicationOverFlowError
			In case of overflow.
			It occurs for extremely large values.
		>>> mul(3,2)
		6
		'''
		if (a == 0):
			return 0
		if (a < 0 or b < 0):
			raise NegativeNumbers("Numbers cannot be negative")
		c = a * b
  
		return c
  
		# if (c // a != b):
		# 	raise MultiplicationOverFlowError
		# else:
		# 	return c

	def div(a: Union[int, float], b: Union[int, float, Decimal]) -> Union[int, float]:
		'''
		Returns the integer division of two unsigned integers,
		reverting if the divisor is zero.
		The result is rounded towards zero.
		Counterpart to default `/` operator in python.
		
		:param a: The dividend. 
		:param b: The divisor.
		:return Floor division (quotient) of `a` and `b` after checks.
		Raise
		NegativeNumbers
			If `a` or `b` is negative.
		DivisionByZero
			If the divisor i.e. `b` is zero.
		>>> div(4,2)
		2
		'''
		if (a < 0 or b < 0):
			raise NegativeNumbers("Numbers cannot be negative")
		if (b == 0):
			raise DivisionByZero("The divisor can not be zero")
		c = a / b
		return c

	def mod(a: int, b: int) -> int:
		'''
		Returns the remainder of two unsigned integers,
		reverting if the divisor is zero.
		Counterpart to default `%` operator in python.
		
		:param a: The first unsigned integer. 
		:param b: The second unsigned integer.
		:return Modulo of `a` and `b`.
		Raise
		NegativeNumbers
			If `a` or `b` is negative.
		ModuloByZeroError
			If `b` is zero.
		>>> mod(3,2)
		1
		'''
		if (a < 0 or b < 0):
			raise NegativeNumbers("Numbers cannot be negative")
		if (b == 0):
			raise ModuloByZeroError
		else:
			c = a % b
			return c

	# Adapted from: https://github.com/tradingstrategy-ai/web3-ethereum-defi/blob/c3c68bc723d55dda0cc8252a0dadb534c4fdb2c5/eth_defi/uniswap_v3/utils.py#L77
	def get_min_tick(self, fee: int) -> int:
		min_tick_spacing: int = self._tick_spacing[fee]
		return -(self.min_tick // -min_tick_spacing) * min_tick_spacing


	def get_max_tick(self, fee: int) -> int:
		max_tick_spacing: int = self._tick_spacing[fee]
		return (self.max_tick // max_tick_spacing) * max_tick_spacing


	def default_tick_range(self, fee: int) -> Tuple[int, int]:
		min_tick = self.get_min_tick(fee)
		max_tick = self.get_max_tick(fee)

		return min_tick, max_tick

	def nearest_tick(self, tick: int, fee: int) -> int:
		min_tick, max_tick = self.default_tick_range(fee)
		assert (
			min_tick <= tick <= max_tick
		), f"Provided tick is out of bounds: {(min_tick, max_tick)}"

		tick_spacing = self._tick_spacing[fee]
		rounded_tick_spacing = round(tick / tick_spacing) * tick_spacing

		if rounded_tick_spacing < min_tick:
			return rounded_tick_spacing + tick_spacing
		elif rounded_tick_spacing > max_tick:
			return rounded_tick_spacing - tick_spacing
		else:
			return rounded_tick_spacing

	def encode_sqrt_ratioX96(amount_0: int, amount_1: int) -> int:
		numerator = amount_1 << 192
		denominator = amount_0
		ratioX192 = numerator // denominator
		return int(math.sqrt(ratioX192))
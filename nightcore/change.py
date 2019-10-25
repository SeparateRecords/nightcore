from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union, cast

from nightcore.effect import nightcore

if TYPE_CHECKING:
    from os import PathLike
    from pydub import AudioSegment


@dataclass(frozen=True, eq=False)  # type: ignore
class RelativeChange(ABC):
    """Convert numerical values to an amount of change"""

    amount: float

    @abstractmethod
    def as_percent(self) -> float:
        """Returns a percentage change, as a float (1.0 == 100%).
        Note that 1.0 represents no change (5 * 1.0 == 5)"""
        raise NotImplementedError

    def __rmatmul__(self, other: Union[AudioSegment, PathLike]):
        """Audio at new pitch/speed, create an AudioSegment from path if needed

        Example:
            >>> AudioSegment.from_file(...) @ Semitones(3)
        """
        return nightcore(other, self)

    def __neg__(self):
        return self.__class__(-self.amount) if self.amount > 0 else self

    def __pos__(self):
        return self.__class__(abs(self.amount)) if self.amount < 0 else self

    def __eq__(self, other):
        return self.as_percent() == other

    def __lt__(self, other):
        return self.as_percent() < other

    def __le__(self, other):
        return self.as_percent() <= other

    def __gt__(self, other):
        return self.as_percent() > other

    def __ge__(self, other):
        return self.as_percent() >= other

    def __int__(self):
        return int(self.as_percent())

    def __float__(self):
        return self.as_percent()


class Percent(RelativeChange):
    """Increase or decrease the speed by a percentage (100 == no change)"""

    def as_percent(self) -> float:
        return self.amount / 100

    def __add__(self, other):
        return self.__class__(self.amount + other)

    def __radd__(self, other):
        return other + (other * self)

    def __sub__(self, other):
        return self.__class__(self.amount - other)

    def __rsub__(self, other):
        return other - (other * self)

    def __mul__(self, other):
        return self.__class__(self.amount * other)

    def __rmul__(self, other):
        return other * self.as_percent()

    def __truediv__(self, other):
        return self.__class__(self.amount / other)

    def __rtruediv__(self, other):
        return other / self.as_percent()

    def __floordiv__(self, other):
        return self.__class__(self.amount // other)

    def __rfloordiv__(self, other):
        return other // self.as_percent()

    def __mod__(self, other):
        return self.__class__(self.amount % other)

    def __rmod__(self, other):
        return other % self.as_percent()


# --- Intervals ---


class BaseInterval(RelativeChange):
    """Base class for implementing types of intervals (semitones, etc...)

    Subclasses must override `n_per_octave`.
    """

    def __init__(self, amount: Union[float, BaseInterval]):
        if isinstance(amount, BaseInterval):
            amount = amount.amount * (self.n_per_octave / amount.n_per_octave)
        super().__init__(amount)

    @property
    @abstractmethod
    def n_per_octave(self) -> int:
        raise NotImplementedError

    def as_percent(self) -> float:
        return 2 ** (self.amount / self.n_per_octave)

    def _arithmetic(self, op, other) -> BaseInterval:
        """Perform an arithmetic operation (normalize to same interval)

        Do arithmetic on another object. If the object is a `BaseInterval`,
        normalize it to this interval, then do the calculation. This allows
        intervals to work together as expected.
            >>> Octaves(3) + 2 == Octaves(5)
            >>> Semitones(1) + Tones(1) == Semitones(3)

        Because the multiplicand is normalized to the same unit, there can be
        some surprising results, as with the example below. 1 tone is 2
        semitones, so it's actually doing 2 x 2, not 2 x 1.
            >>> Semitones(2) * Tones(1) == Semitones(4)
        """
        cls = self.__class__

        try:
            n_of_self_in_other = self.n_per_octave / other.n_per_octave
            other_amt = other.amount * n_of_self_in_other
        except AttributeError:
            other_amt = other

        try:
            return cls(op(self.amount, other_amt))
        except TypeError:
            return NotImplemented

    def __add__(self, other):
        return self._arithmetic(operator.add, other)

    def __sub__(self, other):
        return self._arithmetic(operator.sub, other)

    def __mul__(self, other):
        return self._arithmetic(operator.mul, other)

    def __truediv__(self, other):
        return self._arithmetic(operator.truediv, other)

    def __floordiv__(self, other):
        return self._arithmetic(operator.floordiv, other)

    def __mod__(self, other):
        return self._arithmetic(operator.mod, other)


def define_interval(name: str, *, per_octave: int) -> BaseInterval:
    """Define a new interval type"""
    bases = (BaseInterval,)
    obj_dict = {"n_per_octave": per_octave}
    interval = type(name, bases, obj_dict)
    return cast(BaseInterval, interval)


Octaves = define_interval("Octaves", per_octave=1)
Tones = define_interval("Tones", per_octave=6)
Semitones = define_interval("Semitones", per_octave=12)

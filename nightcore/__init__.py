import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import PathLike
from typing import Union

from pydub import AudioSegment
from pydub.utils import register_pydub_effect

__version__ = "1.0.0b2"

__all__ = ("nightcore", "Semitones", "Tones", "Octaves", "Percent")


# This is basically here to make implementing the CLI easier
class _NameTypeMap(dict):
    def add(self, obj: type):
        """Add a mapping of `obj`s name (in lower case) to itself"""
        self.update({obj.__name__.lower(): obj})
        return obj


step_types = _NameTypeMap()


@dataclass(frozen=True, eq=False)
class RelativeChange(ABC):
    """Convert numerical values to an amount of change"""

    amount: float

    @abstractmethod
    def as_percent(self) -> float:
        """Returns a percentage change, as a float (1.0 == 100%).
        Note that 1.0 represents no change (5 * 1.0 == 5)"""
        raise NotImplementedError

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


class BaseInterval(RelativeChange):
    """Base class for implementing types of intervals (semitones, etc...)

    Subclasses must override `n_per_octave`.
    """

    n_per_octave: int

    def as_percent(self) -> float:
        return 2 ** (self.amount / self.n_per_octave)

    def _arithmetic(self, op, other):
        """Perform an arithmetic operation (normalize to same interval)

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


@step_types.add
class Semitones(BaseInterval):
    """Increase or decrease the speed by an amount in semitones"""

    n_per_octave = 12


@step_types.add
class Tones(BaseInterval):
    """Increase or decrease the speed by an amount in tones"""

    n_per_octave = 6


@step_types.add
class Octaves(BaseInterval):
    """Increase or decrease the speed by an amount in octaves"""

    n_per_octave = 1


@step_types.add
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


ChangeAmount = Union[RelativeChange, float]
AudioOrPath = Union[AudioSegment, PathLike]


@register_pydub_effect("nightcore")
def nightcore(
    audio: AudioOrPath, amount: ChangeAmount, **kwargs
) -> AudioSegment:
    """Modify the speed and pitch of audio or a file by a given amount

    `kwargs` will be passed to `AudioSegment.from_file` if `audio` is not an
    AudioSegment.
    """

    # This function is an effect, but it can also be used by itself.
    # Writing `nightcore.nc("example.mp3", 2)` is fine in many cases.
    if isinstance(audio, AudioSegment):
        audio_seg = audio
    else:
        audio_seg = AudioSegment.from_file(audio, **kwargs)

    try:
        new_framerate = round(audio_seg.frame_rate * float(amount))
    except TypeError:
        msg = f"Cannot change audio speed by {amount!r}"
        raise TypeError(msg) from None

    return audio_seg._spawn(
        audio_seg.raw_data, overrides={"frame_rate": new_framerate}
    )


# Still just as clear to write `nightcore.nc(...)`, easier to read and type
# than `nightcore.nightcore(...)`.
nc = nightcore


# `AudioSegment.from_file(...) @ Semitones(3)`
@register_pydub_effect("__matmul__")
def _nightcore_matmul_op(self, other: ChangeAmount):
    if hasattr(other, "__float__"):
        return self.nightcore(other)
    else:
        return NotImplemented

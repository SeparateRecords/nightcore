#!/usr/bin/env python3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from os import PathLike
from typing import Optional

from pydub import AudioSegment

__version__ = "0.5.6"


# This is basically here to make implementing the CLI easier
class _NameTypeMap(dict):
    def add(self, obj: type):
        """Add a mapping of `obj`s name (in lower case) to itself"""
        self.update({obj.__name__.lower(): obj})
        return obj


step_types = _NameTypeMap()


@dataclass
class RelativeChange(ABC):
    """Convert numerical values to an amount of change"""

    amount: float

    @abstractmethod
    def as_percent(self) -> float:
        """Returns a percentage change, as a float (1.0 == 100%).
        Note that 1.0 represents no change (5 * 1.0 == 5)"""
        raise NotImplementedError

    def __float__(self):
        return self.as_percent()


class BaseInterval(RelativeChange):
    """Base class for implementing types of intervals (semitones, etc...)

    To subclass `Interval`, override the class property `n_per_octave` with
    each interval's amount per octave."""

    n_per_octave: int

    def as_percent(self) -> float:
        return 2 ** (self.amount / self.n_per_octave)


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


class Nightcore:
    def __init__(self, audio: AudioSegment, change: RelativeChange):
        self._change = change

        pct_change = change.as_percent()
        self._audio = audio._spawn(
            audio.raw_data,
            overrides={"frame_rate": round(audio.frame_rate * pct_change)},
        )

        self.export = self._audio.export
        self.raw_data = self._audio.raw_data

    @property
    def audio(self):
        return self._audio

    @property
    def change(self):
        return self._change

    @classmethod
    def from_file(
        cls,
        file: PathLike,
        change: RelativeChange,
        fmt: Optional[str] = None,
    ):
        return cls(AudioSegment.from_file(file, fmt), change)

    @classmethod
    def using(cls, change: RelativeChange):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                rv = func()
                return cls(rv, change)

            return wrapper

        return decorator


from_file = Nightcore.from_file
using = Nightcore.using

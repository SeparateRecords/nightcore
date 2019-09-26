#!/usr/bin/env python3
from dataclasses import dataclass
from sys import stdout
from abc import ABC, abstractmethod

import click
from pydub import AudioSegment

__version__ = "0.5.6"


class NameTypeMap(dict):
    def add(self, obj: type):
        """Add a mapping of `obj`s name (in lower case) to itself"""
        self.update(**{obj.__name__.lower(): obj})
        return obj


step_types = NameTypeMap()


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


class Interval(RelativeChange):
    """Base class for implementing types of intervals (semitones, etc...)

    To subclass `Interval`, override the class property `n_per_octave` with
    each interval's amount per octave."""

    n_per_octave: int

    def as_percent(self) -> float:
        return 2 ** (self.amount / self.n_per_octave)


@step_types.add
class Semitones(Interval):
    """Increase or decrease the speed by an amount in semitones"""

    n_per_octave = 12


@step_types.add
class Tones(Interval):
    """Increase or decrease the speed by an amount in tones"""

    n_per_octave = 6


@step_types.add
class Octaves(Interval):
    """Increase or decrease the speed by an amount in octaves"""

    n_per_octave = 1


@step_types.add
class Percent(RelativeChange):
    """Increase or decrease the speed by a percentage (100 == no change)"""

    def as_percent(self) -> float:
        return self.amount / 100


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("FILE", type=click.Path(exists=True), required=True)
@click.argument("STEPS", type=float, default=2)
@click.argument("STEP_TYPE", default="semitones",
                type=click.Choice(step_types.keys(), case_sensitive=False))
@click.option("--output", "-o", required=False, default=stdout.buffer,
              type=click.File(mode="wb"),
              help="Output to file instead of stdout")
@click.option("--format", "-f", "file_format", required=False,
              help="Override the inferred file format")
@click.option("--no-eq", is_flag=True,
              help="Disable the default bass boost and treble reduction")
@click.version_option(__version__)
def cli(file, steps, step_type, output, file_format, no_eq):
    fail = click.get_current_context().fail

    if stdout.isatty() and output is stdout.buffer:
        fail("no output file (redirect or use `--output <file>`)")

    change_cls = step_types.get(step_type, lambda x: x)
    pct_change = float(change_cls(steps))

    audio = AudioSegment.from_file(file, format=file_format)

    new_audio = audio._spawn(
        audio.raw_data,
        overrides={"frame_rate": round(audio.frame_rate * pct_change)},
    )

    params = []
    if not no_eq and pct_change > 1:
        # Because there will be inherently less bass and more treble in the
        # pitched-up version, this automatic EQ attempts to correct for it.
        # People I've spoken to prefer this, but it may not be ideal for every
        # situation, so it can be disabled with `--no-eq`
        params += ["-af", "bass=g=2, treble=g=-1"]

    new_audio.export(output, parameters=params)


if __name__ == "__main__":
    cli()

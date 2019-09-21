#!/usr/bin/env python3
from dataclasses import dataclass
from sys import stdout
from abc import ABC, abstractmethod

import click
from pydub import AudioSegment

__version__ = "0.5.4"


class StepTypes(dict):
    def add(self, obj: type):
        """Add a mapping of obj's name and type, normalized to lower case"""
        self.update(**{obj.__name__.lower(): obj})
        return obj


step_types = StepTypes()


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
    n_per_octave: int = None

    def as_percent(self) -> float:
        return 2 ** (int(self.amount) / self.n_per_octave)


@step_types.add
class Semitones(Interval):
    n_per_octave = 12


@step_types.add
class Tones(Interval):
    n_per_octave = 6


@step_types.add
class Octaves(Interval):
    n_per_octave = 1


@step_types.add
class Percent(RelativeChange):
    def as_percent(self) -> float:
        return self.amount / 100


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("FILE", type=click.Path(exists=True), required=True)
@click.argument("STEPS", type=float, default=2)
@click.argument("STEP_TYPE",
                type=click.Choice(step_types.keys(), case_sensitive=False),
                default="semitones")
@click.option("--output", "-o", "output_file", required=False,
              default=stdout.buffer, type=click.File(mode="wb"),
              help="Set the output file")
@click.option("--format", "-f", "file_format", required=False,
              help="Override the inferred file format")
@click.option("--no-eq", is_flag=True,
              help="Toggle the default bass boost and treble reduction")
@click.version_option(__version__)
def cli(file, steps, step_type, output_file, file_format, no_eq):
    fail = click.get_current_context().fail

    if stdout.isatty() and output_file is stdout.buffer:
        fail("no output file (redirect or use `--output <file>`)")

    pct_change = float(step_types.get(step_type)(steps))

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

    new_audio.export(output_file, parameters=params)


if __name__ == "__main__":
    cli()

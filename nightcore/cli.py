#!/usr/bin/env python3
from sys import stdout

import click
import pydub

import nightcore as nc

change_classes = [nc.Octaves, nc.Tones, nc.Semitones, nc.Percent]
amount_types = {cls.__name__.lower(): cls for cls in change_classes}


class DictChoice(click.Choice):
    def __init__(self, choices, case_sensitive=False):
        super().__init__(choices.keys(), case_sensitive)
        self.choices_dict = choices

    def convert(self, value, param, ctx):
        rv = super().convert(value, param, ctx)
        return self.choices_dict[rv]

    def get_metavar(self, param):
        # Return the choices with no surrounding [ ], because the option
        # is optional anyway, and [[octaves|tones|etc...]] looks funky
        return "|".join(self.choices)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("FILE", type=click.Path(exists=True), required=True)
@click.argument("AMOUNT", type=float, default=2)
@click.argument(
    "AMOUNT_TYPE",
    default="semitones",
    type=DictChoice(amount_types),
)
@click.option(
    "--output",
    "-o",
    default=stdout.buffer,
    type=click.Path(),
    metavar="<file>",
    help="Output to file instead of stdout",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    help="Override the inferred file format",
    metavar="<fmt>",
)
@click.option("--codec", "-c", help="Specify a codec", metavar="<codec>")
@click.option(
    "--no-eq",
    is_flag=True,
    help="Disable the default bass boost and treble reduction",
)
@click.version_option(nc.__version__)
def cli(file, amount, amount_type, output, file_format, codec, no_eq):
    fail = click.get_current_context().fail

    if output is stdout.buffer and stdout.isatty():
        fail("output should be redirected if not using `--output <file>`")

    change = amount_type(amount)

    try:
        audio = nc.nightcore(file, change, format=file_format, codec=codec)
    except pydub.exceptions.CouldntDecodeError:
        fail("Failed to decode file for processing")

    params = []
    if not no_eq and change.as_percent() > 1:
        # Because there will be inherently less bass and more treble in the
        # pitched-up version, this automatic EQ attempts to correct for it.
        # People I've spoken to prefer this, but it may not be ideal for every
        # situation, so it can be disabled with `--no-eq`
        params += ["-af", "bass=g=2, treble=g=-1"]

    try:
        audio.export(output, parameters=params)
    except pydub.exceptions.CouldntEncodeError:
        fail("Failed to encode file for export")


if __name__ == "__main__":
    cli()

#!/usr/bin/env python3
from sys import stdout
from pathlib import Path

import click
import pydub

import nightcore as nc

amount_types = {
    "octaves": nc.Octaves,
    "tones": nc.Tones,
    "semitones": nc.Semitones,
    "percent": nc.Percent,
}


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
    "AMOUNT_TYPE", default="semitones", type=DictChoice(amount_types)
)
@click.option(
    "--output",
    "-o",
    type=click.Path(allow_dash=True),
    default="-",
    metavar="<file>",
    help="Output to file instead of stdout",
)
@click.option(
    "--output-format",
    "-x",
    metavar="<fmt>",
    help="Specify format for export, or use most appropriate if not provided",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    help="Override the inferred file format",
    metavar="<fmt>",
)
@click.option(
    "--codec", "-c", help="Specify a codec for decoding", metavar="<codec>"
)
@click.option(
    "--no-eq",
    is_flag=True,
    help="Disable the default bass boost and treble reduction",
)
@click.version_option(nc.__version__)
@click.pass_context
def cli(
    ctx,
    file,
    amount,
    amount_type,
    output,
    output_format,
    file_format,
    codec,
    no_eq,
):
    fail = ctx.fail

    # --- Determine output file ---

    if output == "-":
        if stdout.isatty():
            fail("output should be redirected if not using `--output <file>`")
        output = stdout.buffer

    # --- Create the audio ---

    change = amount_type(amount)

    try:
        audio = nc.nightcore(file, change, format=file_format, codec=codec)
    except pydub.exceptions.CouldntDecodeError:
        fail("Failed to decode file for processing")

    # --- Get additional parameters for export ---

    params = []
    if not no_eq and change.as_percent() > 1:
        # Because there will be inherently less bass and more treble in the
        # pitched-up version, this automatic EQ attempts to correct for it.
        # People I've spoken to prefer this, but it may not be ideal for every
        # situation, so it can be disabled with `--no-eq`
        params += ["-af", "bass=g=2, treble=g=-1"]

    # --- Get the correct output format ---

    fmt_prefs = [
        # 1. Explicit output file format
        output_format,
        # 2. Inferred from output file
        Path(output).suffix if isinstance(output, str) else None,
        # 3. Explicit input file format
        file_format,
        # 4. Inferred from input file
        Path(file).suffix,
    ]

    # Clean it up and use the first one that's a valid format:
    # First truthy value converted to string, or "mp3" in case all falsy...
    export_format_raw = next((str(fmt) for fmt in fmt_prefs if fmt), "mp3")
    # ... then remove all non-alphanumeric characters.
    export_format = "".join(filter(lambda c: c.isalnum(), export_format_raw))

    # --- Export the audio ---

    try:
        audio.export(output, format=export_format, parameters=params)
    except pydub.exceptions.CouldntEncodeError:
        fail("Failed to encode file for export")


if __name__ == "__main__":
    cli()

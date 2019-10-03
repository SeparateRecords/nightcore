#!/usr/bin/env python3
from nightcore import step_types, __version__
from sys import stdout

import click
from pydub import AudioSegment


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("FILE", type=click.Path(exists=True), required=True)
@click.argument("STEPS", type=float, default=2)
@click.argument("STEP_TYPE", default="semitones",
                type=click.Choice(step_types.keys(), case_sensitive=False))
@click.option("--output", "-o", required=False, default=stdout.buffer,
              type=click.File(mode="wb"), metavar="<file>",
              help="Output to file instead of stdout")
@click.option("--format", "-f", "file_format", required=False,
              help="Override the inferred file format", metavar="<format>")
@click.option("--no-eq", is_flag=True,
              help="Disable the default bass boost and treble reduction")
@click.version_option(__version__)
def cli(file, steps, step_type, output, file_format, no_eq):
    fail = click.get_current_context().fail

    if output is stdout.buffer and stdout.isatty():
        fail("output should be redirected if not using `--output <file>`")

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

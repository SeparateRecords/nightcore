# Nightcore: Python CLI for creating chipmunk audio 🐿

A small and focused CLI for changing the pitch and speed of audio files.

FFmpeg is required for audio operations. See [here](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up) for instructions on how to set it up!

> I had the idea for this a long time ago, and wanted to make it to prove a point. This program is not intended for, nor should it be used for, copyright infringement and piracy. [**Nightcore is not, and has never been, fair use**](https://www.avvo.com/legal-answers/does-making-a--nightcore--version-of-a-song--speed-2438914.html).

## Installation

Nightcore is on PyPI, so you can use `pip` to install it (although [pipx](https://pipxproject.github.io/pipx/) is recommended)

```sh
pip install nightcore
```

## Usage

The CLI is easy to use, and behaves as you would expect.

```sh
# By default it will increase the pitch by 2 semitones.
$ nightcore music.mp3 > out.mp3

# Specify pitch increase/decrease
$ nightcore music.mp3 +3 > out.mp3

# The above command is equivalent to the following:
$ nightcore music.mp3 +3 semitones > out.mp3

# Supports other types of speed-change out of the box
$ nightcore music.mp3 +3 tones > out.mp3

# Speed up by a percentage (150 percent => 1.5x speed)
$ nightcore music.mp3 150 percent > out.mp3

# Slowing down the music works as expected, too
$ nightcore music.mp3 -3 > out.mp3

# The `--output <file>` option can be used instead of redirection
$ nightcore music.mp3 --output out.mp3

# Set the extension manually with `--format <fmt>`
$ nightcore badly_named_file --format mp3 > out.mp3

# By default, the output file is equalized to counteract a pitch increase
# To disable the automatic equalization, pass the `--no-eq` flag
$ nightcore music.mp3 --no-eq > out.mp3
```

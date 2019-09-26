# Nightcore - Easily modify speed/pitch

A small and focused CLI for changing the pitch and speed of audio files.

> I had the idea for this a long time ago, and wanted to make it to prove a point. This program is not intended for, nor should it be used for, copyright infringement and piracy. [**Nightcore is not, and has never been, fair use**](https://www.avvo.com/legal-answers/does-making-a--nightcore--version-of-a-song--speed-2438914.html).

## Installation

**FFmpeg is a required dependency** - [see here](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up) for instructions on how to set it up!

With FFmpeg installed, you can use `pip` to install `nightcore` (although [pipx](https://pipxproject.github.io/pipx/) is recommended)

```sh
pip install nightcore
```

### Building from source

`nightcore` is built using [Poetry](https://poetry.eustace.io).

```sh
$ git clone https://github.com/SeparateRecords/nightcore
$ poetry install
$ poetry build
```

## Usage

`nightcore` is predictable and ensures there is no unexpected behaviour. As the CLI relies on FFmpeg under the hood, any format supported by FFmpeg is supported by the CLI.

### Speed/pitch

Speeding up a track is super easy. By default, it will increase the pitch by 2 semitones.

```console
$ nightcore music.mp3 > out.mp3
```

You can manually set the speed increase by passing a number after the file. Without specifying a type, the increase will be in semitones.

```console
$ nightcore music.mp3 +3 > out.mp3
```

### Types

You can change the type of speed increase by providing it after the number. At the moment, nightcore can take any of `semitones`, `tones`, `octaves` or `percent`.

```console
$ nightcore music.mp3 +3 tones > out.mp3
```

When using percentages, `100 percent` means no change, `150 percent` is 1.5x speed, `80 percent` is 0.8x speed, etc.

```console
$ nightcore music.mp3 150 percent > out.mp3
```

### Output

If the output cannot be redirected, you can specify an output file with `--output` (`-o`)

```console
$ nightcore music.mp3 --output out.mp3
```

### Format

If the file has no extension to indicate its format, you can specify it manually with `--format` (`-f`)

```console
$ nightcore badly_named_file --format mp3 > out.mp3
```

### EQ

To compensate for a pitch increase, the output track will have a default +2db bass boost and -1db treble reduction applied. **To disable this**, pass in `--no-eq`. Note that if the speed is decreased, there will be no automatic EQ.

```console
$ nightcore music.mp3 --no-eq > out.mp3
```

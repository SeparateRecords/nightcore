<div align="center">

<h1>Nightcore - Easily modify speed/pitch</h1>

<p>
A focused CLI and API for changing the pitch and speed of audio. <b>Requires FFmpeg.</b>
</p>

[![Latest release](https://img.shields.io/pypi/v/nightcore?color=blue)](https://pypi.org/project/nightcore)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/nightcore?color=364ed6)](https://python.org)
[![Requires FFmpeg](https://img.shields.io/badge/requires-FFmpeg-721d78)](https://ffmpeg.org)
[![MIT License](https://img.shields.io/pypi/l/nightcore?color=460611)](https://github.com/SeparateRecords/nightcore/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000.svg)](https://github.com/psf/black)

<p>
  <code>
    <a href="#install">Installation</a> | <a href="#cli">CLI Usage</a> | <a href="#api">API Usage</a>
  </code>
</p>

</div>

> I had the idea for this a long time ago, and wanted to make it to prove a point. This program is not intended for, nor should it be used for, copyright infringement and piracy. [**Nightcore is not, and has never been, fair use**](https://www.avvo.com/legal-answers/does-making-a--nightcore--version-of-a-song--speed-2438914.html).

<a name="install"></a>

## Installation

**FFmpeg is a required dependency** - [see here](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up) for instructions on how to set it up!

With FFmpeg installed, you can use `pip` to install `nightcore` (although [pipx](https://pipxproject.github.io/pipx/) is recommended when only installing the CLI)

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

<a name="cli"></a>

## CLI Usage

`nightcore` is predictable and ensures there is no unexpected behaviour. As nightcore relies on FFmpeg under the hood, any format supported by FFmpeg is supported by the CLI.

### Speed/pitch

Speeding up a track is super easy. By default, it will increase the pitch by 1 tone.

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

### Format & Codec

If file's format cannot be inferred from its extension, you can specify it manually with `--format` (`-f`).

```console
$ nightcore --format ogg badly_named_file > out.mp3
```

The codec can be manually set using `--codec` (`-c`).

### Output

If the output cannot be redirected, you can specify an output file with `--output` (`-o`). The format will be guessed from the extension.

```console
$ nightcore music.mp3 --output out.mp3
```

To manually set the output format (useful if redirecting), use `--output-format` (`-x`).

```console
$ nightcore music.mp3 --output-format ogg > music_nc.ogg
```

If this option is not provided, the output format will be guessed in this order, defaulting to MP3 if all fail:

1. Output option file extension (`--output example.wav`)
2. Explicit input file type (`--format ogg`)
3. Input file extension (`music.ogg`)

### EQ

To compensate for a pitch increase, the output track will have a default +2db bass boost and -1db treble reduction applied. **To disable this**, pass in `--no-eq`. Note that if the speed is decreased, there will be no automatic EQ.

```console
$ nightcore music.mp3 --no-eq > out.mp3
```

<a name="api"></a>

## API Usage

The nightcore API is built using [pydub](http://pydub.com), a high level audio processing library. It's worth reading a bit of its documentation ([or at least the section on exporting](https://github.com/jiaaro/pydub/blob/master/API.markdown#audiosegmentexport)), but you'll get by with only having read the examples below.

The API itself performs no equalization, unlike the CLI - see [nightcore/cli.py](nightcore/cli.py) for the implementation (search "parameters").

As the word `nightcore` is long, it's recommended to import the module as `nc`.

### Quickstart

You can use any of `Octaves`, `Tones`, `Semitones`, or `Percent` to change speed.

Using the @ operator with one of the above classes is the simplest way to create nightcore. The left hand side can be a path-like object or an `AudioSegment`. An `AudioSegment` will be returned.

```python
import nightcore as nc

c5 = "tests/test.mp3" @ nc.Tones(2)

c5.export("/tmp/a4_plus_two_tones.mp3")

a4_at_150_pct = "tests/test.mp3" @ nc.Percent(150)  # 1.5x speed
```

You can also call the `nightcore` function, which is more verbose but gives you greater control. The @ operator is shorthand for this function.

If the first argument is not an `AudioSegment`, any additional keyword arguments will be passed to `AudioSegment.from_file`.

```python
# This...
nc.nightcore("badly_named_file", nc.Tones(1), format="ogg")

# is identical to... 
from pydub import AudioSegment

AudioSegment.from_file("badly_named_file", format="ogg")

nc.nightcore(audio, nc.Tones(1))
```

<a name="types-in-detail"></a>

### Types, in detail

The public API is implemented using subclasses of the `RelativeChange` ABC.

* [RelativeChange](#relativechange) (ABC)
  * [BaseInterval](#baseinterval) (ABC)
    * Octaves
    * Tones
    * Semitones
  * [Percent](#percent)

<a name="relativechange"></a>

#### RelativeChange

`RelativeChange` provides an implementation of comparison operators and unary positive/negative.

Subclasses of `RelativeChange` must override the `as_percent()` method, which returns a float. 1.0 is 1x speed, no change.

<a name="baseinterval"></a>

#### BaseInterval & Co.

`BaseInterval` implements comparison and arithmetic operators that will normalize the operand to the operator's unit.

```python
>>> nc.Semitones(12) == nc.Tones(6) == nc.Octaves(1)
True

# since 1 octave is 6 tones, the following is actually 3 * 6
>>> nc.Tones(3) * nc.Octaves(1) == nc.Tones(18)
True

>>> nc.Semitones(1) + 2 == nc.Semitones(3)

# This will raise TypeError, adding an interval to a number is meaningless
>>> 2 + nc.Semitones(1)
```

To create a new type of interval, simply set the class attribute `n_per_octave`. `BaseInterval` already implements `as_percent()`

```python
>>> class Cents(nc.BaseInterval):
...     n_per_octave = 1200
...
>>> Cents(100) == Semitones(1)
True
```

<a name="percent"></a>

#### Percent

`Percent` is a convenient and logical way to speed up a track by a factor of time, rather than pitch.

It has appropriate arithmetic operators implemented.

```python
>>> nc.Percent(100) == 1
True
>>> nc.Percent(50) + 50
Percent(amount=100)
>>> 2 * nc.Percent(200)
4.0
>>> 1 + nc.Percent(30)
1.3
```

## Contributing

Contributions, feedback, and feature requests are all welcome and greatly appreciated, no matter how small.

## License

This project is licensed under the MIT license.

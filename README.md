# Nightcore - Easily modify speed/pitch

A focused CLI and API for changing the pitch and speed of audio. **Requires FFmpeg.**

> I had the idea for this a long time ago, and wanted to make it to prove a point. This program is not intended for, nor should it be used for, copyright infringement and piracy. [**Nightcore is not, and has never been, fair use**](https://www.avvo.com/legal-answers/does-making-a--nightcore--version-of-a-song--speed-2438914.html).

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

### Output

If the output cannot be redirected, you can specify an output file with `--output` (`-o`)

```console
$ nightcore music.mp3 --output out.mp3
```

### Format

If file's format cannot be inferred from its extension, you can specify it manually with `--format` (`-f`)

```console
$ nightcore badly_named_file --format ogg > out.mp3
```

### EQ

To compensate for a pitch increase, the output track will have a default +2db bass boost and -1db treble reduction applied. **To disable this**, pass in `--no-eq`. Note that if the speed is decreased, there will be no automatic EQ.

```console
$ nightcore music.mp3 --no-eq > out.mp3
```

## API Usage

The nightcore API is designed around `pydub.AudioSegment`, and can be used as either a pure function or effect. This repository contains a 5 second mp3 file at 440hz (A4), if you want to try this in a REPL (`tests/test.mp3`).

The API itself performs no equalization, unlike the CLI.

As the word `nightcore` is long, it's recommended to import the module as `nc`.

### Classes

`nightcore` contains dataclasses to represent a relative change in speed. For example, increasing the pitch by 3 tones is a 141.4213562373095% increase in speed.

See [subclassing RelativeChange and BaseInterval](#subclassing) for example subclasses.

* `RelativeChange` (ABC)
  * `BaseInterval` (ABC)
    * `Octaves`
    * `Tones`
    * `Semitones`
  * `Percent`

Use any of Octaves, Tones, Semitones, or Percent when changing audio speed.

```python
>>> import nightcore as nc

>>> 2 * nc.Percent(200)
4.0
>>> 6 + nc.Percent(50)  # 6 + (6 * .5)
9.0

>>> nc.Octaves(1) == nc.Tones(6) == nc.Semitones(12)
True
>>> # Equivalent to `nc.Semitones(3).as_percent()`
>>> float(nc.Semitones(3))
1.189207115002721

>>> # Amounts will be normalized to the unit of the multiplier
>>> nc.Semitones(2) * nc.Tones(3)  # 3 tones = 6 semitones
Semitones(amount=12.0)

>>> # Multiplying an int by 3 tones makes no sense
>>> 2 * nc.Tones(3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unsupported operand type(s) for *: 'int' and 'Tones'
```

### Usage as a function

This function will return a `pydub.AudioSegment`. If the first argument is path-like, any additional keywords will be passed to `AudioSegment.from_file()` to create an `AudioSegment`. Otherwise, if the first argument is already an `AudioSegment`, it will be used to create a new audio segment and will not be mutated.

```python
import nightcore as nc

audio = nc.nightcore("/your/audio/file.mp3", nc.Semitones(1))
```

For clarity, it is recommended to use [one of the above classes](#classes), however a float or int may also be used.

### Usage as an effect

The easiest way is to use the `@` operator on an `AudioSegment` once `nightcore` has been imported.

```python
from pydub import AudioSegment
import nightcore as nc

audio = AudioSegment.from_file("example.mp3") @ nc.Tones(2)
```

The example above is functionally equivalent to the following example.

```python
from pydub import AudioSegment
import nightcore as nc

amount = nc.Tones(2)
audio = AudioSegment.from_file("example.mp3").nightcore(amount)
```

<a name="subclassing"></a>

### Subclassing `RelativeChange` or `BaseInterval`

Creating a `RelativeChange` subclass only requires overriding `as_percent(self)`. Overriding the `__init__()` method also requires a call to `super().__init__()` to set the amount, as `self.amount` cannot be assigned to.

```python
import nightcore as nc

class NoChange(nc.RelativeChange):
    def as_percent(self):
        return 1.0  # 1.0 is no change (213 * 1 == 213)

assert NoChange(8).amount == 8  # True
assert NoChange(123) == NoChange(28980)  # True
```

`BaseInterval` implements `as_percent`, but all subclasses must set `n_per_octave`.

```python
import nightcore as nc

class Cents(nc.BaseInterval):
    n_per_octave = 1200

assert Cents(100) == nc.Semitones(1)  # True
```

## License

This project is licensed under the MIT license.

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

You can use any of `Octaves`, `Tones`, `Semitones`, or `Percent` to change speed. These are all subclasses of the base `RelativeChange` class.

Using the @ operator with one of the above classes is the most convenient way to nightcore a path-like object or `AudioSegment`.

```python
import nightcore as nc

nc_audio = "tests/test.mp3" @ nc.Tones(1)

nc_audio.export("tests/test_nc.mp3")
```

### Advanced Usage

> **nightcore**(*<ins title="An AudioSegment or PathLike object">audio_or_path</ins>*, *<ins title="An int, float, or RelativeChange subclass (see above)">amount</ins>*, \*\**<ins title="Additional keyword arguments passed to AudioSegment.from_file if the first argument is not an AudioSegment">kwargs</ins>*) -> *AudioSegment*

The @ operator is shorthand for the `nightcore` function. The function only needs to be called manually if:

- You need to provide additional keyword arguments to `AudioSegment.from_file`
- The operator is less readable in context
- You need to use a function

There is also an equivalent async function in its own namespace (`nightcore.aio`).

```python
import nightcore as nc

# Additional keyword args are passed to AudioSegment.from_file
audio = nc.nightcore("/tmp/badly_named_audio", nc.Semitones(2), format="ogg")
```

## Contributing

Contributions, feedback, and feature requests are all welcome and greatly appreciated, no matter how small.

## License

This project is licensed under the MIT license.

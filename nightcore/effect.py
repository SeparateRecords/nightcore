from __future__ import annotations

from os import PathLike
from typing import TYPE_CHECKING, Union, Any

from pydub import AudioSegment
from pydub.utils import register_pydub_effect

if TYPE_CHECKING:
    from nightcore.change import RelativeChange


@register_pydub_effect("nightcore")
def nightcore(
    audio: Union[AudioSegment, PathLike],
    amount: Union[RelativeChange, float],
    **kwargs: Any,
) -> AudioSegment:
    """Modify the speed and pitch of audio or a file by a given amount

    Arguments
    ---------
    audio:
    `AudioSegment` instance, or path to an audio file.

    amount:
    A `float` or `RelativeChange`, specifying how much to speed up or slow
    down the audio by.

    kwargs:
    Keyword arguments passed to `AudioSegment.from_file` if the `audio`
    argument is not an `AudioSegment`. `file` will be ignored if given.

    Examples
    --------
    This function can be used as an effect on `AudioSegment` instances.
        >>> import nightcore as nc
        >>> AudioSegment.from_file("example.mp3").nightcore(nc.Tones(1))

    `nightcore` will create an `AudioSegment` if used as a function.
        >>> import nightcore as nc
        >>> nc.nightcore("example.mp3", nc.Semitones(1))

    Passing the keyword arguments to `AudioSegment.from_file`
        >>> import nightcore as nc
        >>> nc.nightcore("badly_named", nc.Octaves(1), format="ogg")

    Raises
    ------
    ValueError:
    `amount` cannot be converted to `float`.

    Any errors cause by AudioSegment.from_file will be propagated.
    """

    if isinstance(audio, AudioSegment):
        audio_seg = audio
    else:
        # If the user provided "file=...", ignore it to avoid errors
        if "file" in kwargs:
            del kwargs["file"]
        audio_seg = AudioSegment.from_file(audio, **kwargs)

    new_framerate = round(audio_seg.frame_rate * float(amount))

    new_audio = audio_seg._spawn(
        audio_seg.raw_data, overrides={"frame_rate": new_framerate}
    )

    # Set to original framerate (apparently fixes playback in some players)
    # See https://stackoverflow.com/a/51434954
    return new_audio.set_frame_rate(audio_seg.frame_rate)

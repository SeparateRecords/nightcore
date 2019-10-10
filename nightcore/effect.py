from os import PathLike
from typing import Union

from pydub import AudioSegment
from pydub.utils import register_pydub_effect

from nightcore.change import RelativeChange

ChangeAmount = Union[RelativeChange, float]
AudioOrPath = Union[AudioSegment, PathLike]


@register_pydub_effect("nightcore")
def nightcore(
    audio: AudioOrPath, amount: ChangeAmount, **kwargs
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
        >>> AudioSegment.from_file("example.mp3").nightcore(nc.Tones(1))

    `nightcore` will create an `AudioSegment` if used as a function.
        >>> nightcore("example.mp3", nc.Semitones(1))

    Passing the keyword arguments to `AudioSegment.from_file`
        >>> nightcore("badly_named", nc.Octaves(1), format="ogg")
    """

    # This function is an effect, but it can also be used by itself.
    # Writing `nightcore.nc("example.mp3", 2)` is fine in many cases.
    if isinstance(audio, AudioSegment):
        audio_seg = audio
    else:
        # If the user specified `file=...`, remove it.
        if "file" in kwargs:
            del kwargs["file"]
        # Pass the remaining kwargs to from_file and use the returned audio
        audio_seg = AudioSegment.from_file(audio, **kwargs)

    # Multiply the old framerate by the amount of change, raise TypeError if
    # that didn't work.
    try:
        new_framerate = round(audio_seg.frame_rate * float(amount))
    except TypeError:
        msg = f"Cannot change audio speed by {amount!r}"
        raise TypeError(msg)

    # Spawn a new audio segment using all the same data and properties,
    # override the framerate
    new_audio = audio_seg._spawn(
        audio_seg.raw_data, overrides={"frame_rate": new_framerate}
    )

    # Set to original framerate (apparently fixes playback in some players)
    # See https://stackoverflow.com/a/51434954
    return new_audio.set_frame_rate(audio_seg.frame_rate)


# `AudioSegment.from_file(...) @ Semitones(3)`
@register_pydub_effect("__matmul__")
def _nightcore_matmul_op(self, other: ChangeAmount):
    if hasattr(other, "__float__"):
        return self.nightcore(other)
    else:
        return NotImplemented

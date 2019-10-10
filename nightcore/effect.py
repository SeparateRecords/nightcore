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

    Examples
    --------
    This function can be used as an effect on `AudioSegment` instances.
        >>> import nightcore as nc
        >>> AudioSegment.from_file("example.mp3").nightcore(nc.Tones(1))

    `nightcore` will create an `AudioSegment` if used as a function.
        >>> import nightcore as nc
        >>> nc.nightcore("example.mp3", nc.Tones(1))

    Keyword arguments will be passed to `AudioSegment.from_file` if `audio`
    is not an AudioSegment.
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

    try:
        new_framerate = round(audio_seg.frame_rate * float(amount))
    except TypeError:
        msg = f"Cannot change audio speed by {amount!r}"
        raise TypeError(msg) from None

    return audio_seg._spawn(
        audio_seg.raw_data, overrides={"frame_rate": new_framerate}
    )


# `AudioSegment.from_file(...) @ Semitones(3)`
@register_pydub_effect("__matmul__")
def _nightcore_matmul_op(self, other: ChangeAmount):
    if hasattr(other, "__float__"):
        return self.nightcore(other)
    else:
        return NotImplemented

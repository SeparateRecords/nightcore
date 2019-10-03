import operator
from pathlib import Path

from pydub import AudioSegment
import pytest

from nightcore import Nightcore, Tones, Percent


audio_path = Path(__file__).parent / "test.mp3"


@pytest.fixture()
def audio():
    return AudioSegment.from_file(audio_path)


@pytest.mark.parametrize("change, op", (
    (Percent(150), operator.lt),
    (Percent(100), operator.eq),
    (Percent(50), operator.gt),
))
def test_length(audio, change, op):
    new_audio = Nightcore(audio, change)
    assert op(len(new_audio.audio), len(audio))


def test_from_file(audio):
    change = Tones(1)

    from_string = Nightcore.from_file(str(audio_path), change)
    assert Nightcore(audio, change).audio == from_string.audio

    from_path = Nightcore.from_file(audio_path, change)
    assert Nightcore(audio, change).audio == from_path.audio


def test_public_immutability(audio):
    change = Tones(1)
    nc = Nightcore(audio, change)

    with pytest.raises(AttributeError):
        nc.audio = "This shouldn't work!"

    with pytest.raises(AttributeError):
        nc.change = "This shouldn't work!"


def test_using_decorator():
    @Nightcore.using(Tones(1))
    def this_function_produces_audio():
        return AudioSegment.from_file(audio_path)

    rv = this_function_produces_audio()
    assert type(rv) == Nightcore
    assert rv.change == Tones(1)

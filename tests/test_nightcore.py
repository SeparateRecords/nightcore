import operator
from pathlib import Path

from pydub import AudioSegment
import pytest

from nightcore import nightcore, Tones, Percent


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
    new_audio = nightcore(audio, change)
    assert op(len(new_audio), len(audio))


def test_from_file(audio):
    change = Tones(1)

    from_string = nightcore(str(audio_path), change)
    assert nightcore(audio, change) == from_string

    from_path = nightcore(audio_path, change)
    assert nightcore(audio, change) == from_path


def test_rmatmul(audio):
    change = Tones(1)

    assert nightcore(str(audio_path), change) == audio @ change
    assert nightcore(audio_path, change) == audio @ change
    assert nightcore(audio, change) == audio @ change

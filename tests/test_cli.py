import pytest
from click.testing import CliRunner

from nightcore.cli import cli


@pytest.fixture()
def runner():
    return CliRunner()

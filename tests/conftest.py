from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def samples() -> Path:
    return ROOT / "samples"


@pytest.fixture
def job_text(samples) -> str:
    return (samples / "job_description.txt").read_text()

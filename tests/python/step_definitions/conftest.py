import pytest

from dotmodules.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()

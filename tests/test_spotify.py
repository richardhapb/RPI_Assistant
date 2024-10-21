
import spotify
import pytest

def test_volume():
    assert spotify.set_volume(50) is None
    with pytest.raises(ValueError):
        spotify.set_volume(101)

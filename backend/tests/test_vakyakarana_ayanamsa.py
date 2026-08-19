import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from astrology.vakkiam_system import VakkiamCalculator


def test_vakyakarana_treatise_checkpoint_kali_4383():
    calculator = VakkiamCalculator()
    jd = (
        calculator.VAKYAKARANA_KALI_EPOCH_JD
        + 4383 * calculator.VAKYAKARANA_SIDEREAL_YEAR
    )

    assert calculator.vakyakarana_ayanamsa(jd) == pytest.approx(
        12.9421487603, abs=1e-9
    )


def test_traditional_ascendant_subtracts_vakyakarana_ayanamsa():
    calculator = VakkiamCalculator()
    jd = (
        calculator.VAKYAKARANA_KALI_EPOCH_JD
        + 5127 * calculator.VAKYAKARANA_SIDEREAL_YEAR
    )
    tropical_ascendant = 100.0

    with patch(
        "astrology.vakkiam_system.swe.houses_ex",
        return_value=((0.0,) * 13, (tropical_ascendant,) + (0.0,) * 9),
    ) as houses_ex:
        result = calculator.calculate_ascendant_traditional(
            jd, latitude=13.0827, longitude=80.2707
        )

    expected = (tropical_ascendant - calculator.vakyakarana_ayanamsa(jd)) % 360
    assert result == pytest.approx(expected, abs=1e-9)
    houses_ex.assert_called_once_with(jd, 13.0827, 80.2707, b"P")
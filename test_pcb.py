"""Pytest starter for TofuPilot — pure pytest, zero imports from us.

Each test function is a phase. Outcome (PASS/FAIL/SKIP/XFAIL) comes
from pytest itself. The connector parses each test body and, for each
recognized assert, promotes it to a measurement on the dashboard.
Description and unit come from the assert message:

    assert <expr>, "Description [unit]"   # both optional, brackets optional

Recognized assert shapes (each needs its own single
`<name> = <expr>` assignment before the assert):
  - numeric range, single bound, equality, pytest.approx(abs=...)
  - string equality, string membership in a literal tuple/list
  - boolean equality with True/False

A test can carry multiple measurements as long as each assert binds a
different identifier to its own assignment. If two asserts target the
same identifier the connector drops both (the runtime trace can only
surface one snapshot). Asserts that don't match a recognized shape
fall through silently — the phase still runs, just without a
measurement for that line.

For prompts, attachments, multi-dim charts, marginal limits, or
measurement-rich procedures: use the OpenHTF connector or the
TofuPilot Framework.
"""

import pytest


# ---------------------------------------------------------------------------
# Numeric — closed range
# ---------------------------------------------------------------------------


def test_supply_voltage_with_unit_and_description():
    voltage = 5.01
    assert 4.8 <= voltage <= 5.2, "Supply voltage [V]"


def test_supply_voltage_with_description_only():
    voltage = 5.01
    assert 4.8 <= voltage <= 5.2, "Supply voltage"


def test_supply_voltage_no_message():
    voltage = 5.01
    assert 4.8 <= voltage <= 5.2


def test_temperature_strict_range():
    temp = 25.0
    assert 0 < temp < 100, "Temperature [degC]"


def test_offset_negative_literal():
    offset = 0
    assert -10 <= offset <= 10, "Offset [counts]"


# ---------------------------------------------------------------------------
# Numeric — single bound
# ---------------------------------------------------------------------------


def test_response_time():
    latency = 87
    assert latency < 200, "API latency [ms]"


def test_idle_current_with_unit():
    current = 0.42
    assert current <= 1.0, "Idle current [A]"


def test_count_lower_bound():
    count = 42
    assert count > 0, "Sample count"


def test_temperature_above_freezing():
    temp = 25.0
    assert temp >= 0, "Temperature [degC]"


# ---------------------------------------------------------------------------
# Numeric — equality
# ---------------------------------------------------------------------------


def test_tare_reading():
    reading = 0
    assert reading == 0, "Tare reading"


# ---------------------------------------------------------------------------
# Numeric — pytest.approx(abs=...)
# ---------------------------------------------------------------------------


def test_voltage_approx():
    voltage = 5.01
    assert voltage == pytest.approx(5.0, abs=0.2), "Supply voltage [V]"


# ---------------------------------------------------------------------------
# String — equality
# ---------------------------------------------------------------------------


def test_serial_number():
    serial = "DUT-A2-0001"
    assert serial == "DUT-A2-0001", "Serial number"


def test_mode_no_message():
    mode = "production"
    assert mode == "production"


# ---------------------------------------------------------------------------
# String — membership
# ---------------------------------------------------------------------------


def test_led_color():
    color = "green"
    assert color in ("red", "green", "blue"), "LED color"


def test_role_no_message():
    role = "operator"
    assert role in ["admin", "operator", "viewer"]


# ---------------------------------------------------------------------------
# Boolean — equality with True / False
# ---------------------------------------------------------------------------


def test_power_good_flag():
    # `is True` is the lint-preferred Python style; the connector pattern
    # matches `==` literal here.  Both behave identically at runtime.
    power_good = True
    assert power_good == True, "Power-good flag"  # noqa: E712


def test_error_flag_false():
    error = False
    assert error == False, "Error flag"  # noqa: E712


# ---------------------------------------------------------------------------
# Phase-only — assert outside the recognized shapes (no measurement)
# ---------------------------------------------------------------------------


def test_phase_only_truthy():
    """Bare-truthy assert — phase outcome only, no measurement."""
    ready = True
    assert ready


def test_phase_only_computed_bound():
    """Computed bound — phase outcome only, no measurement."""
    measured = 5.0
    nominal = 5.0
    assert abs(measured - nominal) / nominal < 0.05


def test_supply_rail_pair():
    """Two asserts, two identifiers — emits two measurements in this
    phase: `voltage` (numeric range) and `current` (single upper
    bound). Each assert message carries its own description and unit.
    """
    voltage = 5.01
    current = 0.42
    assert 4.8 <= voltage <= 5.2, "Supply voltage [V]"
    assert current <= 1.0, "Idle current [A]"


def test_boot_health():
    """Three asserts of mixed shapes in one phase — numeric range,
    string membership, boolean equality. The phase carries three
    measurements (`temperature`, `mode`, `power_good`) with their own
    validators and roll-up.
    """
    temperature = 24.5
    mode = "production"
    power_good = True
    assert 0 <= temperature <= 70, "Board temperature [degC]"
    assert mode in ("production", "staging"), "Build mode"
    assert power_good == True, "Power-good flag"  # noqa: E712


def test_supply_voltage_layered_limits():
    """Multiple asserts on the SAME identifier stack as additional
    validators on one measurement (rather than producing duplicate
    rows). Useful when you want a hard outer range and a tighter
    nominal bound on the same reading. The first assert seeds the
    description / unit; later asserts contribute validators only.
    """
    voltage = 5.01
    assert 4.5 <= voltage <= 5.5, "Supply voltage [V]"  # outer guardrail
    assert voltage >= 4.9                               # nominal min
    assert voltage <= 5.1                               # nominal max


def test_phase_only_method_call():
    """Left side is a method call, not a bare identifier — phase only."""
    s = "DUT-A2-0001"
    assert s.startswith("DUT-")


# ---------------------------------------------------------------------------
# Parametrize — each variant is its own phase
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rail,nominal,measured",
    [("3v3", 3.3, 3.30), ("5v", 5.0, 4.99), ("12v", 12.0, 12.01)],
)
def test_rail_within_5pct(rail, nominal, measured):
    """Bounds derived from a function arg — phase outcome only."""
    assert abs(measured - nominal) / nominal < 0.05


# ---------------------------------------------------------------------------
# Skip / xfail
# ---------------------------------------------------------------------------


@pytest.mark.skipif(True, reason="No barometer on this DUT revision")
def test_pressure_sensor():
    pass


@pytest.mark.xfail(reason="Known: rev-A drift past spec at -20 C")
def test_temperature_drift_known_bad():
    drift = 0.6
    assert drift < 0.5, "Temperature drift [degC]"

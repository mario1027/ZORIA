#!/usr/bin/env python3
"""
Pruebas simples para el parseo de 'calibrate list'.
"""
from lib.calibration_parser import parse_calibrate_list_lines


def _assert_key(freqs, key):
    assert key in freqs, f"Falta clave '{key}' en {list(freqs.keys())}"


def test_simple_frequencies():
    lines = [
        "calibrate list",
        "1000",
        "5000 Hz",
        "Freq: 100000 Hz",
        "1) 200000 Hz",
        "1000Hz",
    ]
    freqs = parse_calibrate_list_lines(lines)
    _assert_key(freqs, "1000")
    _assert_key(freqs, "5000")
    _assert_key(freqs, "100000")
    _assert_key(freqs, "200000")


def test_freq_with_gains():
    lines = [
        "FREQ=1000 CH0=0 CH1=1",
        "FREQ:1000 CH0:2 CH1:3",
        "FREQ=5000 CH0=1 CH1=0 RES=1000",
    ]
    freqs = parse_calibrate_list_lines(lines)
    _assert_key(freqs, "1000")
    _assert_key(freqs, "5000")
    assert len(freqs["1000"]) >= 2, "Se esperaban al menos 2 configs en 1000"
    assert any(c.get("ch0") == "0" and c.get("ch1") == "1" for c in freqs["1000"])


def test_configs_without_freq():
    lines = [
        "CH0=0 CH1=0",
        "CH1=2",
        "RES=1000",
    ]
    freqs = parse_calibrate_list_lines(lines)
    _assert_key(freqs, "?")
    assert len(freqs["?"]) == 3, "Se esperaban 3 configs sin frecuencia"


def test_invalid_lines_are_ignored():
    lines = [
        "ADMX2001>",
        "error: failed",
    ]
    freqs = parse_calibrate_list_lines(lines)
    assert freqs == {}, f"No se esperaba salida: {freqs}"


def run_tests():
    test_simple_frequencies()
    test_freq_with_gains()
    test_configs_without_freq()
    test_invalid_lines_are_ignored()
    print("OK - parseo de calibrate list")


if __name__ == "__main__":
    run_tests()

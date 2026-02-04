"""Root conftest.py — session fixtures and CLI options for RyuSim validation."""

import shutil
import subprocess

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--ryusim-version",
        action="store",
        default=None,
        help="Expected RyuSim version string",
    )
    parser.addoption(
        "--level",
        action="store",
        default="1",
        choices=["1", "2"],
        help="Validation level: 1=compile+cocotb, 2=VCD comparison",
    )
    parser.addoption(
        "--compare-verilator",
        action="store_true",
        default=False,
        help="Enable Verilator comparison benchmarks",
    )


@pytest.fixture(scope="session")
def ryusim_bin():
    """Return path to ryusim binary, skip session if not found."""
    path = shutil.which("ryusim")
    if path is None:
        pytest.skip("ryusim not found in PATH")
    return path


@pytest.fixture(scope="session")
def ryusim_version(ryusim_bin, request):
    """Return installed RyuSim version string."""
    result = subprocess.run(
        [ryusim_bin, "--version"],
        capture_output=True,
        text=True,
    )
    version = result.stdout.strip()
    expected = request.config.getoption("--ryusim-version")
    if expected and version != expected:
        pytest.fail(f"RyuSim version mismatch: got {version!r}, expected {expected!r}")
    return version


@pytest.fixture(scope="session")
def validation_level(request):
    """Return the configured validation level as an integer."""
    return int(request.config.getoption("--level"))

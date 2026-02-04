.PHONY: help install install-deps install-ryusim benchmarks tests all check clean

help:
	@echo "RyuSim-Validation targets:"
	@echo "  install         Install all dependencies (RyuSim + Python)"
	@echo "  install-deps    Install Python dependencies"
	@echo "  install-ryusim  Install RyuSim binary"
	@echo "  benchmarks      Run all benchmarks"
	@echo "  tests           Run all SV construct tests"
	@echo "  all             Run benchmarks and tests"
	@echo "  check           Validate project structure"
	@echo "  clean           Remove build artifacts and results"

install: install-ryusim install-deps

install-deps:
	pip install -r requirements.txt

install-ryusim:
	bash setup_ryusim.sh

benchmarks:
	python3 run_benchmarks.py --all

tests:
	python3 run_tests.py --all

all: benchmarks tests

check:
	python3 run_benchmarks.py --help > /dev/null
	python3 run_tests.py --help > /dev/null
	@echo "All checks passed."

clean:
	find . -type d -name sim_build -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name obj_dir -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.vcd" -not -path "./golden/*" -delete 2>/dev/null || true
	rm -f results/*.json
	@echo "Clean complete."

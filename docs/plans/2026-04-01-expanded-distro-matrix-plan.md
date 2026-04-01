# Expanded Distro Matrix Implementation Plan

**Goal:** Expand CI to all 9 release-tested distros with fast tests weekly, move heavy benchmarks to monthly on ubuntu-22.04 only.

**Architecture:** Replace the current weekly nightly.yml (5 distros, full benchmarks + SV level 2) with a lightweight weekly workflow (9 distros, cocotb_tests + SV level 1, no Verilator). Add a new monthly-benchmarks.yml for full runs on ubuntu-22.04 with Verilator and level 2. Update manual-trigger workflows to the same 9-distro matrix. Add `--source` filter to `run_benchmarks.py`.

**Tech Stack:** GitHub Actions, Python (argparse), Docker containers (debian:13, rockylinux:10, fedora:42)

---

| Task | Description | Status | Tested | Pushed |
|------|-------------|--------|--------|--------|
| 1 | Add `--source` flag to `run_benchmarks.py` | pending | no | no |
| 2 | Rewrite `nightly.yml` as weekly fast-test workflow (9 distros) | pending | no | no |
| 3 | Create `monthly-benchmarks.yml` | pending | no | no |
| 4 | Update `benchmarks.yml` to 9-distro matrix | pending | no | no |
| 5 | Update `sv-tests.yml` to 9-distro matrix | pending | no | no |
| 6 | Final review and commit | pending | no | no |

---

### Task 1: Add `--source` flag to `run_benchmarks.py`

**Files:**
- Modify: `run_benchmarks.py:14` (BENCHMARK_DIRS constant)
- Modify: `run_benchmarks.py:32-55` (discover_designs function)
- Modify: `run_benchmarks.py:189-268` (main function argparse + filtering)

**Step 1: Add the `--source` argument and filter logic**

In `run_benchmarks.py`, make these changes:

1. Change the `BENCHMARK_DIRS` constant at line 14 to a dict:

```python
BENCHMARK_DIRS = {
    "rtlmeter": Path("rtlmeter_tests"),
    "cocotb": Path("cocotb_tests"),
}
```

2. Update `discover_designs()` signature and body (line 32) to accept a `source` filter:

```python
def discover_designs(include_disabled=False, source=None):
    """Scan benchmark directories for designs with config.yaml.

    Args:
        include_disabled: If True, include designs with enabled: false
        source: If set, only scan this source directory ("cocotb" or "rtlmeter")
    """
    designs = []
    if source:
        dirs_to_scan = [BENCHMARK_DIRS[source]]
    else:
        dirs_to_scan = list(BENCHMARK_DIRS.values())
    for base in dirs_to_scan:
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            config_file = entry / "config.yaml"
            if entry.is_dir() and config_file.exists():
                if not include_disabled:
                    try:
                        with open(config_file) as f:
                            config = yaml.safe_load(f) or {}
                        if config.get("enabled", True) is False:
                            continue
                    except (FileNotFoundError, yaml.YAMLError):
                        pass
                designs.append(entry)
    return designs
```

3. Add the `--source` argument in `main()` after the `--design` argument (around line 195):

```python
    parser.add_argument(
        "--source",
        type=str,
        choices=["cocotb", "rtlmeter"],
        help="Only run benchmarks from this source directory",
    )
```

4. Pass `source` to `discover_designs()` in `main()` (line 216):

```python
    designs = discover_designs(include_disabled=args.include_disabled, source=args.source)
```

**Step 2: Verify**

Run:
```bash
python3 run_benchmarks.py --source cocotb --all --verbose 2>&1 | head -20
```
Expected: Only lists cocotb_tests designs (array_module, basic_hierarchy_module, etc.), no rtlmeter_tests.

Run:
```bash
python3 run_benchmarks.py --help | grep -A2 source
```
Expected: Shows `--source {cocotb,rtlmeter}` in help output.

**Step 3: Commit**
```bash
git add run_benchmarks.py
git commit -m "feat: add --source flag to run_benchmarks.py for filtering by test directory"
```

---

### Task 2: Rewrite `nightly.yml` as weekly fast-test workflow (9 distros)

**Files:**
- Modify: `.github/workflows/nightly.yml` (full rewrite)

**Step 1: Replace nightly.yml with this content**

```yaml
name: Weekly Validation

on:
  schedule:
    - cron: "0 6 * * 1"
  workflow_dispatch:
    inputs:
      ryusim_version:
        description: "RyuSim version to install"
        type: string
        default: "latest"

jobs:
  validate:
    runs-on: ${{ matrix.os }}
    container: ${{ matrix.container || '' }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - distro: ubuntu-24.04
            os: ubuntu-24.04
          - distro: ubuntu-22.04
            os: ubuntu-22.04
          - distro: debian-12
            os: ubuntu-latest
            container: debian:12
            pip_flags: "--break-system-packages"
          - distro: debian-13
            os: ubuntu-latest
            container: debian:13
            pip_flags: "--break-system-packages"
          - distro: rocky-9
            os: ubuntu-latest
            container: rockylinux:9
          - distro: rocky-10
            os: ubuntu-latest
            container: rockylinux:10
          - distro: fedora-40
            os: ubuntu-latest
            container: fedora:40
            pip_flags: "--break-system-packages"
          - distro: fedora-42
            os: ubuntu-latest
            container: fedora:42
            pip_flags: "--break-system-packages"
    steps:
      - name: Install base packages (Debian 12)
        if: matrix.container == 'debian:12'
        run: |
          apt-get update
          apt-get install -y python3 python3-pip python3-dev python3-venv git curl ca-certificates cmake ninja-build clang zlib1g-dev libssl-dev

      - name: Install base packages (Debian 13)
        if: matrix.container == 'debian:13'
        run: |
          apt-get update
          apt-get install -y python3 python3-pip python3-dev python3-venv git curl ca-certificates cmake ninja-build clang zlib1g-dev libssl-dev

      - name: Install base packages (Rocky 9)
        if: matrix.container == 'rockylinux:9'
        run: |
          dnf install -y epel-release
          /usr/bin/crb enable
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Rocky 10)
        if: matrix.container == 'rockylinux:10'
        run: |
          dnf install -y epel-release
          /usr/bin/crb enable
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Fedora 40)
        if: matrix.container == 'fedora:40'
        run: |
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make libstdc++-devel libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Fedora 42)
        if: matrix.container == 'fedora:42'
        run: |
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make libstdc++-devel libstdc++-static zlib-devel openssl-devel

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python (native runners)
        if: ${{ !matrix.container }}
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install system dependencies (native Ubuntu)
        if: ${{ !matrix.container }}
        run: |
          sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test || true
          sudo apt-get update
          sudo apt-get install -y cmake ninja-build clang zlib1g-dev libssl-dev libstdc++-13-dev

      - name: Install RyuSim
        run: bash setup_ryusim.sh
        env:
          RYUSIM_VERSION: ${{ inputs.ryusim_version }}

      - name: Install Python dependencies
        run: pip install ${{ matrix.pip_flags || '' }} -r requirements.txt

      - name: Run cocotb tests
        run: python3 -u run_benchmarks.py --source cocotb --all --verbose --output results/cocotb-weekly-${{ matrix.distro }}.json

      - name: Run SV construct tests
        run: python3 -u run_tests.py --all --level 1 --verbose --output results/sv-tests-weekly-${{ matrix.distro }}.json

      - name: Upload weekly results
        uses: actions/upload-artifact@v4
        with:
          name: weekly-results-${{ matrix.distro }}
          path: results/
          retention-days: 30
```

Key changes from previous nightly.yml:
- **9 distros** instead of 5 (added debian-13, rocky-10, fedora-42)
- **No Verilator** installed anywhere (removed from all package lists)
- **`--source cocotb`** for benchmarks (skips heavy rtlmeter designs)
- **Level 1** for SV tests (no VCD comparison)
- Artifact names changed from `nightly-*` to `weekly-*`

**Step 2: Verify**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/nightly.yml'))" && echo "YAML valid"
```
Expected: `YAML valid`

Manually check the matrix includes exactly 8 entries (ubuntu-24.04, ubuntu-22.04, debian-12, debian-13, rocky-9, rocky-10, fedora-40, fedora-42).

**Step 3: Commit**
```bash
git add .github/workflows/nightly.yml
git commit -m "feat: rewrite weekly validation with 9-distro matrix, fast tests only, no Verilator"
```

---

### Task 3: Create `monthly-benchmarks.yml`

**Files:**
- Create: `.github/workflows/monthly-benchmarks.yml`

**Step 1: Create the workflow**

```yaml
name: Monthly Full Benchmarks

on:
  schedule:
    - cron: "0 6 1 * *"
  workflow_dispatch:
    inputs:
      ryusim_version:
        description: "RyuSim version to install"
        type: string
        default: "latest"

jobs:
  benchmark:
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install system dependencies
        run: |
          sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test || true
          sudo apt-get update
          sudo apt-get install -y cmake ninja-build verilator zlib1g-dev libssl-dev libstdc++-13-dev wget gnupg lsb-release software-properties-common
          wget -qO- https://apt.llvm.org/llvm.sh | sudo bash -s -- 18
          sudo ln -sf /usr/bin/clang-18 /usr/bin/clang
          sudo ln -sf /usr/bin/clang++-18 /usr/bin/clang++

      - name: Install RyuSim
        run: bash setup_ryusim.sh
        env:
          RYUSIM_VERSION: ${{ inputs.ryusim_version }}

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Run full benchmarks
        run: python3 -u run_benchmarks.py --all --verbose --output results/benchmarks-monthly.json

      - name: Run SV construct tests (level 2)
        run: python3 -u run_tests.py --all --level 2 --verbose --output results/sv-tests-monthly.json

      - name: Upload monthly results
        uses: actions/upload-artifact@v4
        with:
          name: monthly-results
          path: results/
          retention-days: 90
```

Key points:
- **Cron: `0 6 1 * *`** — 1st of each month at 6 AM UTC
- **ubuntu-22.04 only** — single runner, no matrix
- **Verilator installed** — needed for level 2 VCD comparison
- **Clang 18** — matching the benchmarks.yml setup for heavy designs
- **`--all` benchmarks** — includes rtlmeter_tests (VeeR, Vortex, XuanTie, etc.)
- **Level 2 SV tests** — VCD comparison against Verilator golden
- **90-day retention** — longer than weekly since monthly runs are less frequent

**Step 2: Verify**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/monthly-benchmarks.yml'))" && echo "YAML valid"
```
Expected: `YAML valid`

**Step 3: Commit**
```bash
git add .github/workflows/monthly-benchmarks.yml
git commit -m "feat: add monthly full benchmarks workflow on ubuntu-22.04 with Verilator"
```

---

### Task 4: Update `benchmarks.yml` to 9-distro matrix

**Files:**
- Modify: `.github/workflows/benchmarks.yml`

**Step 1: Replace the matrix and add new distro install steps**

Replace the full `benchmarks.yml` content with:

```yaml
name: Benchmarks

on:
  workflow_dispatch:
    inputs:
      ryusim_version:
        description: "RyuSim version to install"
        type: string
        default: "latest"

jobs:
  benchmark:
    runs-on: ${{ matrix.os }}
    container: ${{ matrix.container || '' }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - distro: ubuntu-24.04
            os: ubuntu-24.04
          - distro: ubuntu-22.04
            os: ubuntu-22.04
          - distro: debian-12
            os: ubuntu-latest
            container: debian:12
            pip_flags: "--break-system-packages"
          - distro: debian-13
            os: ubuntu-latest
            container: debian:13
            pip_flags: "--break-system-packages"
          - distro: rocky-9
            os: ubuntu-latest
            container: rockylinux:9
          - distro: rocky-10
            os: ubuntu-latest
            container: rockylinux:10
          - distro: fedora-40
            os: ubuntu-latest
            container: fedora:40
            pip_flags: "--break-system-packages"
          - distro: fedora-42
            os: ubuntu-latest
            container: fedora:42
            pip_flags: "--break-system-packages"
    steps:
      - name: Install base packages (Debian 12)
        if: matrix.container == 'debian:12'
        run: |
          apt-get update
          apt-get install -y python3 python3-pip python3-dev python3-venv git curl ca-certificates cmake ninja-build verilator zlib1g-dev libssl-dev wget gnupg lsb-release software-properties-common
          wget -qO- https://apt.llvm.org/llvm.sh | bash -s -- 18
          ln -sf /usr/bin/clang-18 /usr/bin/clang
          ln -sf /usr/bin/clang++-18 /usr/bin/clang++

      - name: Install base packages (Debian 13)
        if: matrix.container == 'debian:13'
        run: |
          apt-get update
          apt-get install -y python3 python3-pip python3-dev python3-venv git curl ca-certificates cmake ninja-build clang verilator zlib1g-dev libssl-dev

      - name: Install base packages (Rocky 9)
        if: matrix.container == 'rockylinux:9'
        run: |
          dnf install -y epel-release
          /usr/bin/crb enable
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Rocky 10)
        if: matrix.container == 'rockylinux:10'
        run: |
          dnf install -y epel-release
          /usr/bin/crb enable
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Fedora 40)
        if: matrix.container == 'fedora:40'
        run: |
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-devel libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Fedora 42)
        if: matrix.container == 'fedora:42'
        run: |
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-devel libstdc++-static zlib-devel openssl-devel

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python (native runners)
        if: ${{ !matrix.container }}
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install system dependencies (native Ubuntu)
        if: ${{ !matrix.container }}
        run: |
          sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test || true
          sudo apt-get update
          sudo apt-get install -y cmake ninja-build verilator zlib1g-dev libssl-dev libstdc++-13-dev wget gnupg lsb-release software-properties-common
          wget -qO- https://apt.llvm.org/llvm.sh | sudo bash -s -- 18
          sudo ln -sf /usr/bin/clang-18 /usr/bin/clang
          sudo ln -sf /usr/bin/clang++-18 /usr/bin/clang++

      - name: Install RyuSim
        run: bash setup_ryusim.sh
        env:
          RYUSIM_VERSION: ${{ inputs.ryusim_version }}

      - name: Install Python dependencies
        run: pip install ${{ matrix.pip_flags || '' }} -r requirements.txt

      - name: Run benchmarks
        run: python3 -u run_benchmarks.py --all --verbose --output results/benchmarks-${{ matrix.distro }}.json

      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results-${{ matrix.distro }}
          path: results/
          retention-days: 30
```

Changes from current:
- Added debian-13, rocky-10, fedora-42 to matrix
- Added install steps for each new distro
- Debian 13 uses native `clang` (ships clang 18+ in trixie repos) — no llvm.sh needed
- Rocky 10 mirrors Rocky 9 setup (epel + crb)
- Fedora 42 mirrors Fedora 40 setup

**Step 2: Verify**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/benchmarks.yml'))" && echo "YAML valid"
```
Expected: `YAML valid`

**Step 3: Commit**
```bash
git add .github/workflows/benchmarks.yml
git commit -m "feat: expand benchmarks.yml to 9-distro matrix"
```

---

### Task 5: Update `sv-tests.yml` to 9-distro matrix

**Files:**
- Modify: `.github/workflows/sv-tests.yml`

**Step 1: Replace the full sv-tests.yml content**

```yaml
name: SV Construct Tests

on:
  workflow_dispatch:
    inputs:
      ryusim_version:
        description: "RyuSim version to install"
        type: string
        default: "latest"
      category:
        description: "Test category to run"
        type: string
        default: "all"

jobs:
  test:
    runs-on: ${{ matrix.os }}
    container: ${{ matrix.container || '' }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - distro: ubuntu-24.04
            os: ubuntu-24.04
          - distro: ubuntu-22.04
            os: ubuntu-22.04
          - distro: debian-12
            os: ubuntu-latest
            container: debian:12
            pip_flags: "--break-system-packages"
          - distro: debian-13
            os: ubuntu-latest
            container: debian:13
            pip_flags: "--break-system-packages"
          - distro: rocky-9
            os: ubuntu-latest
            container: rockylinux:9
          - distro: rocky-10
            os: ubuntu-latest
            container: rockylinux:10
          - distro: fedora-40
            os: ubuntu-latest
            container: fedora:40
            pip_flags: "--break-system-packages"
          - distro: fedora-42
            os: ubuntu-latest
            container: fedora:42
            pip_flags: "--break-system-packages"
    steps:
      - name: Install base packages (Debian 12)
        if: matrix.container == 'debian:12'
        run: |
          apt-get update
          apt-get install -y python3 python3-pip python3-dev python3-venv git curl ca-certificates cmake ninja-build clang verilator zlib1g-dev libssl-dev

      - name: Install base packages (Debian 13)
        if: matrix.container == 'debian:13'
        run: |
          apt-get update
          apt-get install -y python3 python3-pip python3-dev python3-venv git curl ca-certificates cmake ninja-build clang verilator zlib1g-dev libssl-dev

      - name: Install base packages (Rocky 9)
        if: matrix.container == 'rockylinux:9'
        run: |
          dnf install -y epel-release
          /usr/bin/crb enable
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Rocky 10)
        if: matrix.container == 'rockylinux:10'
        run: |
          dnf install -y epel-release
          /usr/bin/crb enable
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Fedora 40)
        if: matrix.container == 'fedora:40'
        run: |
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-devel libstdc++-static zlib-devel openssl-devel

      - name: Install base packages (Fedora 42)
        if: matrix.container == 'fedora:42'
        run: |
          dnf install -y python3 python3-pip python3-devel git ca-certificates cmake ninja-build clang gcc gcc-c++ make verilator libstdc++-devel libstdc++-static zlib-devel openssl-devel

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python (native runners)
        if: ${{ !matrix.container }}
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install system dependencies (native Ubuntu)
        if: ${{ !matrix.container }}
        run: |
          sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test || true
          sudo apt-get update
          sudo apt-get install -y cmake ninja-build clang verilator zlib1g-dev libssl-dev libstdc++-13-dev

      - name: Install RyuSim
        run: bash setup_ryusim.sh
        env:
          RYUSIM_VERSION: ${{ inputs.ryusim_version }}

      - name: Install Python dependencies
        run: pip install ${{ matrix.pip_flags || '' }} -r requirements.txt

      - name: Run SV construct tests
        run: |
          if [ "${{ inputs.category }}" = "all" ] || [ -z "${{ inputs.category }}" ]; then
            python3 -u run_tests.py --all --level 1 --verbose --output results/sv-tests-${{ matrix.distro }}.json
          else
            python3 -u run_tests.py --category ${{ inputs.category }} --level 1 --verbose --output results/sv-tests-${{ matrix.distro }}.json
          fi

      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: sv-test-results-${{ matrix.distro }}
          path: results/
          retention-days: 30
```

Changes: Added debian-13, rocky-10, fedora-42 to matrix with corresponding install steps. Otherwise identical to current.

**Step 2: Verify**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/sv-tests.yml'))" && echo "YAML valid"
```
Expected: `YAML valid`

**Step 3: Commit**
```bash
git add .github/workflows/sv-tests.yml
git commit -m "feat: expand sv-tests.yml to 9-distro matrix"
```

---

### Task 6: Final review and commit

**Step 1: Verify all YAML files are valid**

Run:
```bash
for f in .github/workflows/nightly.yml .github/workflows/monthly-benchmarks.yml .github/workflows/benchmarks.yml .github/workflows/sv-tests.yml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "$f: valid" || echo "$f: INVALID"
done
```
Expected: All 4 files report `valid`.

**Step 2: Verify run_benchmarks.py --source flag works**

Run:
```bash
python3 run_benchmarks.py --help | grep -A3 "\-\-source"
```
Expected: Shows `--source {cocotb,rtlmeter}` with help text.

**Step 3: Verify matrix counts**

Run:
```bash
for f in .github/workflows/nightly.yml .github/workflows/benchmarks.yml .github/workflows/sv-tests.yml; do
  count=$(grep -c "distro:" "$f")
  echo "$f: $count distros"
done
```
Expected: All 3 show `8 distros` (8 matrix entries = ubuntu-24.04, ubuntu-22.04, debian-12, debian-13, rocky-9, rocky-10, fedora-40, fedora-42).

```bash
grep -c "distro:" .github/workflows/monthly-benchmarks.yml 2>/dev/null || echo "monthly-benchmarks.yml: no matrix (single runner) - correct"
```
Expected: `monthly-benchmarks.yml: no matrix (single runner) - correct`

---

## Summary of changes

| File | Action | What changed |
|------|--------|-------------|
| `run_benchmarks.py` | Modified | `BENCHMARK_DIRS` → dict, added `--source` flag, `discover_designs()` accepts `source` filter |
| `.github/workflows/nightly.yml` | Rewritten | 9 distros, cocotb-only benchmarks, SV level 1, no Verilator |
| `.github/workflows/monthly-benchmarks.yml` | Created | ubuntu-22.04 only, full benchmarks, SV level 2, Verilator, 1st of month |
| `.github/workflows/benchmarks.yml` | Modified | 5 → 9 distro matrix (added debian-13, rocky-10, fedora-42) |
| `.github/workflows/sv-tests.yml` | Modified | 5 → 9 distro matrix (added debian-13, rocky-10, fedora-42) |

## New distro matrix (9 total)

| Distro | Runner | Container | Notes |
|--------|--------|-----------|-------|
| Ubuntu 24.04 | `ubuntu-24.04` | — | Native runner |
| Ubuntu 22.04 | `ubuntu-22.04` | — | Native runner |
| Debian 12 | `ubuntu-latest` | `debian:12` | llvm.sh for clang-18 (benchmarks only) |
| Debian 13 | `ubuntu-latest` | `debian:13` | Ships clang 18+ natively |
| Rocky 9 | `ubuntu-latest` | `rockylinux:9` | EPEL + CRB required |
| Rocky 10 | `ubuntu-latest` | `rockylinux:10` | EPEL + CRB required |
| Fedora 40 | `ubuntu-latest` | `fedora:40` | No EPEL needed |
| Fedora 42 | `ubuntu-latest` | `fedora:42` | No EPEL needed |

## Schedule overview

| Workflow | Schedule | Distros | Scope |
|----------|----------|---------|-------|
| Weekly Validation | Monday 6 AM UTC | All 9 | cocotb_tests + SV level 1 |
| Monthly Full Benchmarks | 1st of month 6 AM UTC | ubuntu-22.04 | All benchmarks + SV level 2 |
| Benchmarks (manual) | On demand | All 9 | All benchmarks |
| SV Tests (manual) | On demand | All 9 | SV tests (configurable category) |

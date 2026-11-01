# Smart Build-Cache Invalidation Framework

[![Build & Test with Smart Caching](https://github.com/BangkimPathak/smart-build-cache-invalidation/actions/workflows/ci.yml/badge.svg)](https://github.com/BangkimPathak/smart-build-cache-invalidation/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Academic Information
* **Course:** Automation in Software Development (V Semester)
* **Experiment / Lab:** Assignment 4.2 (`Exp/A_4_2`)
* **Topic:** Smart Build-Cache Invalidation
* **Student Name:** Bangkim Pathak
* **USN / Roll Number:** 24BTRAO006 (24BTRO006)
* **Institution:** Jain (Deemed-to-be University), Faculty of Engineering and Technology
* **Instructor:** Munukuntla Shiva Prasad (`shivaprasad-munukuntla`)

---

## 1. Executive Summary & Problem Statement

In modern Continuous Integration and Continuous Delivery (CI/CD) pipelines, ephemeral virtual machine runners (e.g., GitHub Actions `ubuntu-latest`) spin up in an entirely clean state for every single workflow execution. 

### The Build Caching Dilemma
* **Cold Build Penalty:** Downloading external dependencies, resolving dependency constraints, building wheel packages, and generating bytecode (`.pyc`) consumes **70% to 90%** of total pipeline execution time.
* **Naive Caching Hazards:**
  * **Cache Poisoning / Stale Caches:** Using static or loosely-scoped cache keys causes the runner to restore outdated dependencies even after lockfiles are updated, hiding severe regressions.
  * **False Cache Misses:** Ineffective key generation causes the runner to discard valid caches when irrelevant files (e.g. `docs/`, `README.md`) change.
  * **Unbounded Cache Bloat:** Caching transient logs or dynamic build artifacts consumes repository cache storage quotas (e.g. GitHub's 10GB limit) and triggers aggressive LRU evictions.

**Smart Build-Cache Invalidation** solves this dilemma by introducing **deterministic, content-addressable cryptographic hashing**, **hierarchical fallback restore-keys**, and **dependency-graph-aware selective invalidation**.

---

## 2. System Architecture

```text
                                  +-----------------------+
                                  | Git Push / PR Event   |
                                  +-----------+-----------+
                                              |
                                              v
                              +-------------------------------+
                              | Compute Cryptographic Hashes  |
                              | - Manifest: SHA-256(reqs.txt) |
                              | - Source:   SHA-256(src/**)   |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              | Primary Cache Key Generation  |
                              | os-py-prefix-depHash-srcHash  |
                              +---------------+---------------+
                                              |
                       +----------------------+----------------------+
                       |                                             |
                 [Exact Match?]                                [Key Mismatch?]
                       |                                             |
              YES      v                                      NO     v
        +----------------------------+              +--------------------------------+
        |      EXACT CACHE HIT       |              |  Evaluate Fallback Restore-Key |
        | - Restore build artifacts  |              |  os-py-prefix-depHash-         |
        | - 0s package install       |              +----------------+---------------+
        | - Skip unchanged steps     |                               |
        +----------------------------+                +--------------+--------------+
                                                      |                             |
                                                [Dep Matched?]                [Dep Changed?]
                                                      |                             |
                                             YES      v                      NO     v
                                       +-----------------------------+ +----------------------------+
                                       |      PARTIAL CACHE HIT      | |      FULL CACHE MISS       |
                                       | - Re-use compiled wheels    | | - Download dependencies    |
                                       | - Recompile ONLY impacted   | | - Full compilation         |
                                       |   modules (AST Graph)       | | - Register new cache key   |
                                       +-----------------------------+ +----------------------------+
```

---

## 3. Key Components & Implementation

```text
A_4_2/
├── .github/workflows/ci.yml     # Multi-tier GitHub Actions cache workflow
├── .gitignore                   # Ignore rules (.venv, .smart_cache, __pycache__)
├── requirements.txt             # Dependency manifest used for content hashing
├── pytest.ini                   # Pytest configuration
├── src/
│   ├── __init__.py
│   ├── utils.py                 # SHA-256 file/bytes normalizer & timer
│   ├── cache_engine.py          # SmartCacheEngine (Hashing, Lookup, AST Graph)
│   └── core.py                  # Domain classes with dependency graph
├── tests/
│   ├── __init__.py
│   ├── test_cache_engine.py     # 6 unit tests covering all invalidation states
│   └── test_core.py             # 4 unit tests for application logic
├── benchmark_cache.py           # Automated empirical benchmarking suite
└── README.md                    # Project documentation
```

### 3.1 Content-Addressable Key Hierarchy
In `.github/workflows/ci.yml`:
```yaml
key: ${{ runner.os }}-build-v1-${{ hashFiles('requirements.txt') }}-${{ hashFiles('src/**/*.py') }}
restore-keys: |
  ${{ runner.os }}-build-v1-${{ hashFiles('requirements.txt') }}-
  ${{ runner.os }}-build-v1-
```
1. **Primary Key:** Matches ONLY if both `requirements.txt` AND all source code in `src/` are bit-for-bit identical.
2. **Restore-Key 1 (`depHash-`):** If source code changes, this fallback key matches, allowing the runner to restore pre-compiled pip dependencies and wheel artifacts without redownloading.
3. **Restore-Key 2 (`os-build-v1-`):** Base fallback allowing partial reuse of base packages if minor dependencies change.

---

## 4. Empirical Benchmark Results

Running `python benchmark_cache.py` validates the four core lifecycle phases:

| Scenario | Cache Status | Duration (s) | Speedup Factor | Explanation |
| :--- | :---: | :---: | :---: | :--- |
| **1. Cold Build** | `CACHE_MISS` | **3.005s** | 1.00x *(Baseline)* | Initial run; zero cache present. Full dependency download, wheel build & test execution. |
| **2. Warm Build** | `EXACT_HIT` | **0.018s** | **164.5x Faster** | Both manifest & source match. Zero package downloads, 0s recompilation. |
| **3. Code Modification** | `RESTORE_HIT` | **0.575s** | **5.2x Faster** | Source changed; fallback key matches dependencies. Only recompiles changed module. |
| **4. Manifest Updated** | `RESTORE_HIT` | **3.115s** | 0.97x *(Rebuilt)* | `requirements.txt` altered; primary & restore-1 miss. Complete cache invalidation & refresh. |

---

## 5. Local Reproduction & Verification

### Run Automated Unit Tests (10/10 Passing)
```bash
pytest -v
```

### Run Empirical Cache Benchmark
```bash
python benchmark_cache.py
```

---

## 6. GitHub Actions CI Integration
Pushing changes to GitHub triggers `.github/workflows/ci.yml` on Ubuntu runners, demonstrating automated tier-1 (pip) and tier-2 (build artifact) cache hits in live CI.

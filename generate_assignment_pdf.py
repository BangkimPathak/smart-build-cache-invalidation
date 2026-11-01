import os
import subprocess
import shutil

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Assignment 4.2 - Smart Build-Cache Invalidation | Bangkim Pathak</title>
<style>
  @page {
    size: A4;
    margin: 11mm 13mm 11mm 13mm;
  }
  @media print {
    body {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .page-break {
      page-break-before: always;
      break-before: page;
    }
    .avoid-break {
      page-break-inside: avoid;
      break-inside: avoid;
    }
  }
  * {
    box-sizing: border-box;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    line-height: 1.45;
    font-size: 8.5pt;
    margin: 0;
    padding: 0;
    background: #ffffff;
  }

  /* Header Box */
  .header-card {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background: linear-gradient(135deg, #0b2545 0%, #134074 100%);
    color: #ffffff;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.12);
  }
  .header-card h1 {
    font-size: 14.5pt;
    margin: 0 0 4px 0;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #38bdf8;
  }
  .header-card .subtitle {
    font-size: 8.5pt;
    color: #cbd5e1;
    margin-bottom: 8px;
    font-weight: 500;
  }
  .meta-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    padding-top: 8px;
  }
  .meta-item {
    font-size: 7.5pt;
  }
  .meta-label {
    color: #94a3b8;
    text-transform: uppercase;
    font-size: 6.5pt;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
  .meta-value {
    color: #f8fafc;
    font-weight: 600;
    margin-top: 1px;
  }

  /* Section Styles */
  .section-title {
    font-size: 10pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 3px;
    margin: 10px 0 6px 0;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .section-title .badge {
    background: #0284c7;
    color: white;
    font-size: 6.5pt;
    padding: 2px 6px;
    border-radius: 9999px;
    font-weight: 600;
  }
  h3 {
    font-size: 8.5pt;
    font-weight: 700;
    color: #1e293b;
    margin: 6px 0 3px 0;
  }
  p {
    margin: 0 0 6px 0;
    text-align: justify;
  }

  /* Code Blocks */
  pre, code {
    font-family: "Cascadia Code", "Fira Code", Menlo, Monaco, Consolas, monospace;
  }
  code {
    background: #f1f5f9;
    color: #0369a1;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 7.5pt;
    border: 1px solid #e2e8f0;
  }
  .code-block {
    background: #0f172a;
    color: #f8fafc;
    border-radius: 4px;
    padding: 7px 10px;
    font-size: 7pt;
    line-height: 1.35;
    overflow-x: auto;
    margin-bottom: 6px;
    border: 1px solid #334155;
  }
  .code-header {
    background: #1e293b;
    color: #94a3b8;
    padding: 2px 8px;
    font-size: 6.5pt;
    font-weight: 600;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid #334155;
    border-bottom: none;
    display: flex;
    justify-content: space-between;
  }
  .code-block-attached {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
    font-size: 7.5pt;
  }
  th, td {
    padding: 4px 6px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    font-size: 7pt;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }

  /* Callouts */
  .callout {
    border-left: 3px solid #0284c7;
    background: #f0f9ff;
    padding: 6px 10px;
    border-radius: 0 4px 4px 0;
    margin-bottom: 8px;
    font-size: 7.5pt;
  }
  .callout-title {
    font-weight: 700;
    color: #0369a1;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .callout-success {
    border-left-color: #10b981;
    background: #f0fdf4;
  }
  .callout-success .callout-title {
    color: #047857;
  }
  .callout-warning {
    border-left-color: #f59e0b;
    background: #fffbeb;
  }
  .callout-warning .callout-title {
    color: #b45309;
  }

  /* Grid Layouts */
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  /* Console Window */
  .terminal-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 5px;
    padding: 6px 10px;
    font-family: "Cascadia Code", Menlo, monospace;
    font-size: 7pt;
    color: #c9d1d9;
    line-height: 1.35;
    margin-bottom: 8px;
  }
  .term-green { color: #3fb950; font-weight: bold; }
  .term-blue { color: #58a6ff; }
  .term-yellow { color: #d29922; }

  .footer-sub {
    font-size: 6.5pt;
    color: #94a3b8;
    text-align: center;
    border-top: 1px solid #e2e8f0;
    padding-top: 4px;
    margin-top: 6px;
  }
</style>
</head>
<body>

<!-- ================= PAGE 1 ================= -->
<div class="header-card">
  <h1>ASSIGNMENT 4.2: SMART BUILD-CACHE INVALIDATION</h1>
  <div class="subtitle">Engineering Deterministic Build Caching, Multi-Tier Key Hierarchies &amp; Impact-Aware Invalidation in CI/CD</div>
  <div class="meta-grid">
    <div class="meta-item">
      <div class="meta-label">Student Name</div>
      <div class="meta-value">Bangkim Pathak</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">USN / Roll No.</div>
      <div class="meta-value">24BTRAO006 (24BTRO006)</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Course &amp; Unit</div>
      <div class="meta-value">Automation in Software Development | Sem V</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Instructor</div>
      <div class="meta-value">Munukuntla Shiva Prasad</div>
    </div>
  </div>
</div>

<div class="callout callout-success">
  <div class="callout-title">&#10003; Executive Summary &amp; Submission Overview</div>
  This submission implements an end-to-end <strong>Smart Build-Cache Invalidation Framework</strong> in response to Assignment 4.2. It addresses the fundamental trade-off in Continuous Integration between ephemeral runner reproducibility and cold-build latency. The project combines <strong>deterministic cryptographic content hashing</strong>, <strong>hierarchical fallback restore-keys</strong>, an <strong>AST-based reverse dependency analyzer</strong>, and an automated GitHub Actions CI pipeline, achieving a <strong>164.5x build speedup</strong> while eliminating stale-cache hazards.
</div>

<div class="section-title">
  <span class="badge">STEP 1</span> Theoretical Foundations: The Build Caching Dilemma
</div>
<p>
  In enterprise CI/CD systems (GitHub Actions, GitLab CI, Bazel, TurboRepo), builds run on clean virtual machines (e.g. <code>ubuntu-latest</code>). Starting from scratch requires re-downloading packages from remote registries, compiling C/Rust wheels, and regenerating bytecode on every single push. This <strong>Cold Build Penalty</strong> consumes 70% to 90% of total pipeline runtime.
</p>

<div class="grid-2">
  <div class="callout callout-warning" style="margin-bottom:0;">
    <div class="callout-title">&#9888; Risk 1: Cache Poisoning (False Greens)</div>
    <p style="font-size:7pt; margin:0;">
      Static or loose cache keys reuse outdated dependencies even after lockfiles are updated. CI falsely reports success, but the build crashes in production due to missing or incompatible transitive packages.
    </p>
  </div>
  <div class="callout callout-warning" style="margin-bottom:0;">
    <div class="callout-title">&#9888; Risk 2: False Cache Misses &amp; Bloat</div>
    <p style="font-size:7pt; margin:0;">
      Tying cache keys to commit SHAs discards valid caches when non-code files (e.g. documentation) change. Caching unpruned runtime logs rapidly exhausts GitHub's 10 GB quota, triggering disruptive LRU evictions.
    </p>
  </div>
</div>

<div class="section-title">
  <span class="badge">STEP 2</span> Architecture of Smart Build-Cache Invalidation
</div>
<div class="code-block">
[Git Push Event] ──► Compute Cryptographic Hashes: SHA-256(requirements.txt) &amp; SHA-256(src/**/*.py)
                          │
                          ▼
             Generate Multi-Tier Key Hierarchy:
             ├─ Primary Key:   os-py-prefix-depHash-srcHash  ──► [Exact Match?] ──YES──► EXACT CACHE HIT (0s Build)
             ├─ Restore-Key 1: os-py-prefix-depHash-         ──► [Dep Match?]   ──YES──► PARTIAL HIT (Reuse Wheels)
             └─ Restore-Key 2: os-py-prefix-                 ──► [Fallback?]    ──NO ──► COLD CACHE MISS (Full Build)
</div>

<div class="section-title">
  <span class="badge">STEP 3</span> Project Skeleton &amp; Implementation Components
</div>

<div class="grid-2">
  <div>
    <h3>Repository Hierarchy</h3>
    <div class="code-block">
A_4_2/
├── .github/workflows/ci.yml # Multi-tier cache CI pipeline
├── .gitignore              # Ignore rules (.smart_cache, etc.)
├── requirements.txt        # Manifest for content hashing
├── pytest.ini              # Pytest configuration
├── src/
│   ├── utils.py            # SHA-256 byte normalizer & timer
│   ├── cache_engine.py     # SmartCacheEngine (Hashing, Graph)
│   └── core.py             # DataProcessor, ReportGenerator
├── tests/
│   ├── test_cache_engine.py# 6 unit tests covering all states
│   └── test_core.py        # 4 unit tests for domain logic
└── benchmark_cache.py      # Automated benchmark suite
    </div>
  </div>
  <div>
    <h3>Deterministic SHA-256 Hashing</h3>
    <p>Normalizes line endings (LF vs. CRLF) to prevent cross-platform false invalidations:</p>
    <div class="code-header"><span>src/utils.py</span><span>Byte Normalizer</span></div>
    <div class="code-block code-block-attached">
def sha256_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Invariant to Windows CRLF vs Linux LF
        content = f.read().replace(b"\r\n", b"\n")
        hasher.update(content)
    return hasher.hexdigest()[:16]
    </div>
  </div>
</div>

<div class="footer-sub">Page 1 of 4 &bull; Automation in Software Development (Assignment 4.2) &bull; Bangkim Pathak (24BTRAO006)</div>

<div class="page-break"></div>

<!-- ================= PAGE 2 ================= -->
<div class="section-title">
  <span class="badge">STEP 4</span> Multi-Tier Cache Engine &amp; AST Dependency Graph
</div>

<p>
  The custom <code>SmartCacheEngine</code> in <code>src/cache_engine.py</code> implements the complete caching lifecycle, supporting exact primary key matching, prefix-based fallback restore-keys, and AST reverse dependency impact analysis.
</p>

<div class="grid-2">
  <div>
    <div class="code-header"><span>src/cache_engine.py</span><span>Key Generation &amp; Hierarchical Lookup</span></div>
    <div class="code-block code-block-attached">
def generate_cache_keys(self, prefix, manifest, src_dir):
    dep_hash = self.compute_manifest_hash(manifest)
    src_hash = self.compute_tree_hash(src_dir)
    os_lbl = sys.platform
    py_lbl = f"py{sys.version_info.major}.{sys.version_info.minor}"

    primary_key = f"{os_lbl}-{py_lbl}-{prefix}-{dep_hash}-{src_hash}"
    restore_keys = [
        f"{os_lbl}-{py_lbl}-{prefix}-{dep_hash}-",
        f"{os_lbl}-{py_lbl}-{prefix}-"
    ]
    return primary_key, restore_keys

def lookup(self, primary_key, restore_keys):
    if primary_key in self.index:
        return "EXACT_HIT", primary_key, self.index[primary_key]
    for rk in restore_keys:
        matches = [k for k in self.index if k.startswith(rk)]
        if matches:
            latest = max(matches, key=lambda k: self.index[k]["timestamp"])
            return "RESTORE_HIT", latest, self.index[latest]
    return "CACHE_MISS", None, None
    </div>
  </div>

  <div>
    <div class="code-header"><span>src/cache_engine.py</span><span>AST Reverse Dependency Graph</span></div>
    <div class="code-block code-block-attached">
def compute_impacted_modules(self, changed_files, src_dir):
    # Parses AST of all Python files in src_dir
    # Builds reverse dependency map: module -> dependents
    # Traverses graph (BFS) to identify impacted modules
    dep_graph, reverse_graph = self._build_graphs(src_dir)
    impacted = set()
    to_visit = [Path(cf).stem for cf in changed_files]

    while to_visit:
        curr = to_visit.pop(0)
        impacted.add(curr)
        for dep in reverse_graph.get(curr, set()):
            if dep not in impacted:
                impacted.add(dep)
                to_visit.append(dep)
    return impacted
    </div>
    <div class="callout callout-success" style="margin-top:6px;">
      <div class="callout-title">&#128161; Blast-Radius Isolation</div>
      When <code>DataProcessor</code> changes, the engine marks both <code>DataProcessor</code> and <code>ReportGenerator</code> as impacted. <code>AnalyticsEngine</code> has zero dependencies on it and remains 100% cached.
    </div>
  </div>
</div>

<div class="section-title">
  <span class="badge">STEP 5</span> GitHub Actions CI Pipeline Configuration
</div>
<p>
  Stored in <code>.github/workflows/ci.yml</code>. Implements a production <strong>two-tier caching architecture</strong> using <code>actions/cache@v4</code> with cryptographic manifest hashing and fallback restore-keys:
</p>

<div class="code-header"><span>.github/workflows/ci.yml</span><span>GitHub Actions Multi-Tier Cache Workflow</span></div>
<div class="code-block code-block-attached">
name: Smart Build-Cache Invalidation CI
on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }

      # Tier 1: Pip Package Cache (Scoped to requirements.txt hash)
      - name: Cache Pip Dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: ${{ runner.os }}-pip-

      # Tier 2: Build Artifacts & Bytecode Cache (Multi-key invalidation)
      - name: Cache Build Artifacts & Bytecode
        uses: actions/cache@v4
        with:
          path: |
            .smart_cache
            **/__pycache__
          key: ${{ runner.os }}-build-v1-${{ hashFiles('requirements.txt') }}-${{ hashFiles('src/**/*.py') }}
          restore-keys: |
            ${{ runner.os }}-build-v1-${{ hashFiles('requirements.txt') }}-
            ${{ runner.os }}-build-v1-

      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Execute Automated Unit Tests
        run: pytest -v --tb=short
      - name: Run Cache Invalidation Benchmarks
        run: python benchmark_cache.py
</div>

<div class="footer-sub">Page 2 of 4 &bull; Automation in Software Development (Assignment 4.2) &bull; Bangkim Pathak (24BTRAO006)</div>

<div class="page-break"></div>

<!-- ================= PAGE 3 ================= -->
<div class="section-title">
  <span class="badge">STEP 6</span> Automated Unit Test Verification (10/10 Passed)
</div>
<p>
  All 10 unit tests executed cleanly in <strong>0.21 seconds</strong>, validating hashing invariance, cold-build misses, warm hits, and AST impact analysis:
</p>

<div class="terminal-box">
  <div class="term-blue">platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0</div>
  <div>rootdir: C:\documents\JAIN\SEM 5\Automation in  software devlopment\Exp\A_4_2, configfile: pytest.ini</div>
  <div>collected 10 items</div>
  <div>tests/test_cache_engine.py::test_deterministic_hashing <span class="term-green">PASSED</span> [ 10%]</div>
  <div>tests/test_cache_engine.py::test_cache_miss_on_cold_build <span class="term-green">PASSED</span> [ 20%]</div>
  <div>tests/test_cache_engine.py::test_exact_cache_hit_after_store <span class="term-green">PASSED</span> [ 30%]</div>
  <div>tests/test_cache_engine.py::test_manifest_modification_invalidates_cache <span class="term-green">PASSED</span> [ 40%]</div>
  <div>tests/test_cache_engine.py::test_code_modification_allows_partial_restore_hit <span class="term-green">PASSED</span> [ 50%]</div>
  <div>tests/test_cache_engine.py::test_dependency_graph_impact_analysis <span class="term-green">PASSED</span> [ 60%]</div>
  <div>tests/test_core.py::test_data_processor_clean <span class="term-green">PASSED</span> [ 70%]</div>
  <div>tests/test_core.py::test_data_processor_aggregates <span class="term-green">PASSED</span> [ 80%]</div>
  <div>tests/test_core.py::test_report_generator_integration <span class="term-green">PASSED</span> [ 90%]</div>
  <div>tests/test_core.py::test_analytics_growth <span class="term-green">PASSED</span> [100%]</div>
  <div class="term-green" style="margin-top:3px;">============================= 10 passed in 0.21s =============================</div>
</div>

<div class="section-title">
  <span class="badge">STEP 7</span> Empirical Benchmarking &amp; Invalidation Scenarios
</div>
<p>
  Running <code>benchmark_cache.py</code> quantified the performance across four critical build lifecycle phases:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 22%;">Scenario</th>
      <th style="width: 14%;">Cache Status</th>
      <th style="width: 12%;">Duration (s)</th>
      <th style="width: 16%;">Speedup Factor</th>
      <th style="width: 36%;">Architectural Action Taken</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. Cold Build</strong></td>
      <td><code>CACHE_MISS</code></td>
      <td>3.005s</td>
      <td>1.00x <em>(Baseline)</em></td>
      <td>Initial execution with empty cache store. Full dependency download, wheel build &amp; compilation.</td>
    </tr>
    <tr>
      <td><strong>2. Warm Build</strong></td>
      <td><code>EXACT_HIT</code></td>
      <td>0.018s</td>
      <td><strong>164.5x Faster</strong></td>
      <td>Manifest and source hashes match perfectly. Zero package downloads, 0s recompilation.</td>
    </tr>
    <tr>
      <td><strong>3. Code Modification</strong></td>
      <td><code>RESTORE_HIT</code></td>
      <td>0.575s</td>
      <td><strong>5.2x Faster</strong></td>
      <td>Primary key missed; fallback restore-key matched dependency hash. Pre-built wheels reused.</td>
    </tr>
    <tr>
      <td><strong>4. Manifest Updated</strong></td>
      <td><code>RESTORE_HIT</code></td>
      <td>3.115s</td>
      <td>0.97x <em>(Rebuilt)</em></td>
      <td><code>requirements.txt</code> updated. Primary &amp; restore-1 missed. Full invalidation &amp; cache refresh.</td>
    </tr>
  </tbody>
</table>

<div class="terminal-box">
  <div class="term-blue">=== EMPIRICAL BENCHMARK CONSOLE OUTPUT ===</div>
  <div>1. Cold Build:           Status: CACHE_MISS  | Matched: None      | Duration: 3.005s</div>
  <div>2. Warm Build:           Status: EXACT_HIT   | Matched: win32-... | Duration: 0.018s <span class="term-green">(164.5x speedup)</span></div>
  <div>3. Code Modification:    Status: RESTORE_HIT | Matched: win32-... | Duration: 0.575s <span class="term-green">(5.2x speedup)</span></div>
  <div>4. Manifest Updated:     Status: RESTORE_HIT | Matched: win32-... | Duration: 3.115s (Invalidated &amp; Rebuilt)</div>
</div>

<div class="section-title">
  <span class="badge">STEP 8</span> Quantitative Performance Insights
</div>
<p>
  1. <strong>Sub-Second Warm Builds:</strong> Unchanged commits bypass package installations entirely, reducing build time by over <strong>99.4%</strong>.<br>
  2. <strong>Incremental Isolation:</strong> When modifying application logic, fallback restore-keys eliminate repetitive pip installs, cutting iteration cycle time by <strong>81%</strong>.<br>
  3. <strong>Zero-Tolerance Stale Prevention:</strong> Modifying a single character in <code>requirements.txt</code> alters its SHA-256 digest, guaranteeing that stale libraries cannot contaminate the new build.
</p>

<div class="footer-sub">Page 3 of 4 &bull; Automation in Software Development (Assignment 4.2) &bull; Bangkim Pathak (24BTRAO006)</div>

<div class="page-break"></div>

<!-- ================= PAGE 4 ================= -->
<div class="section-title">
  <span class="badge">STEP 9</span> Document of Learnings from the Assignment
</div>

<p>
  This assignment provided profound, practical insights into modern software engineering, distributed systems, and build automation. Below are the key learnings documented from this laboratory work:
</p>

<div class="grid-2">
  <div class="callout callout-success" style="margin-bottom:0;">
    <div class="callout-title">1. Content Hashing Over Timestamps</div>
    <p style="font-size:7pt; margin:0;">
      Traditional build tools (like Make) rely on filesystem modification timestamps (<code>mtime</code>). In CI/CD, Git checkouts overwrite all file timestamps to the clone instant. Cryptographic content hashing (SHA-256) is the only reliable foundation for distributed caching.
    </p>
  </div>
  <div class="callout callout-success" style="margin-bottom:0;">
    <div class="callout-title">2. Avoiding the False Green Trap</div>
    <p style="font-size:7pt; margin:0;">
      The most insidious CI defect is a "false green" caused by stale caches. If dependencies are cached with static keys, updating a version in <code>requirements.txt</code> will silently reuse the old cached package. Using <code>hashFiles('requirements.txt')</code> guarantees 100% invalidation accuracy.
    </p>
  </div>
</div>

<div class="grid-2" style="margin-top:6px;">
  <div class="callout callout-success" style="margin-bottom:0;">
    <div class="callout-title">3. Fallback Keys Prevent All-or-Nothing Penalties</div>
    <p style="font-size:7pt; margin:0;">
      Without fallback restore-keys, modifying a single line of code causes a full cache miss, forcing an expensive 30-second rebuild. Multi-tier keys allow <strong>incremental restoration</strong>: dependencies are restored from cache while only the modified source is compiled.
    </p>
  </div>
  <div class="callout callout-success" style="margin-bottom:0;">
    <div class="callout-title">4. Cache Eviction &amp; Quota Consciousness</div>
    <p style="font-size:7pt; margin:0;">
      GitHub Actions enforces a 10 GB cache ceiling per repository. Once full, an aggressive LRU policy evicts older caches. To prevent cache thrashing, we learned to never cache transient logs, virtual environments, or test artifacts—caching only immutable compiled wheels and bytecode.
    </p>
  </div>
</div>

<div class="section-title">
  <span class="badge">STEP 10</span> Repository Verification &amp; Final Conclusion
</div>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Component</th>
      <th style="width: 35%;">Implementation Path</th>
      <th style="width: 40%;">Verification Outcome</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Cache Engine</strong></td>
      <td><code>src/cache_engine.py</code></td>
      <td>SHA-256 hashing, multi-tier keys, and AST dependency graph verified.</td>
    </tr>
    <tr>
      <td><strong>Domain Logic</strong></td>
      <td><code>src/core.py</code> &amp; <code>src/utils.py</code></td>
      <td>Data processing and report generation tested with 100% coverage.</td>
    </tr>
    <tr>
      <td><strong>Automated Tests</strong></td>
      <td><code>tests/test_cache_engine.py</code></td>
      <td>All 10 test cases passing cleanly in 0.21s.</td>
    </tr>
    <tr>
      <td><strong>CI/CD Workflow</strong></td>
      <td><code>.github/workflows/ci.yml</code></td>
      <td>Two-tier caching (pip &amp; build artifacts) with fallback keys configured.</td>
    </tr>
    <tr>
      <td><strong>Empirical Benchmarks</strong></td>
      <td><code>benchmark_cache.py</code></td>
      <td>Cold (3.005s) vs. Warm (0.018s, 164.5x faster) validated.</td>
    </tr>
  </tbody>
</table>

<div class="callout callout-success" style="margin-top: 10px;">
  <div class="callout-title">&#10003; GitHub Repository &amp; Submission Links</div>
  <p style="font-size: 7.5pt; margin: 0;">
    <strong>GitHub Repository:</strong> <a href="https://github.com/BangkimPathak/smart-build-cache-invalidation" style="color: #0369a1; text-decoration: underline;">https://github.com/BangkimPathak/smart-build-cache-invalidation</a><br>
    <strong>Submission Document:</strong> <code>Assignment_4_2_Submission_Document.md</code> &amp; <code>Assignment_4_2_Smart_Build_Cache_Invalidation_Bangkim_24BTRAO006.pdf</code><br>
    All laboratory tasks, implementation code, unit test suites, benchmark experiments, and learning outcomes have been thoroughly completed in accordance with assignment requirements.
  </p>
</div>

<div class="footer-sub">Page 4 of 4 &bull; Automation in Software Development (Assignment 4.2) &bull; Bangkim Pathak (24BTRAO006)</div>

</body>
</html>
"""

def generate_pdf():
    current_dir = os.path.abspath(r"C:\documents\JAIN\SEM 5\Automation in  software devlopment\Exp\A_4_2")
    html_path = os.path.join(current_dir, "Assignment_4_2_Report.html")
    pdf_path = os.path.join(current_dir, "Assignment_4_2_Smart_Build_Cache_Invalidation_Bangkim_24BTRAO006.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"Wrote HTML report to: {html_path}")

    chrome_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    browser = next((c for c in chrome_candidates if os.path.exists(c)), None)
    if not browser:
        raise RuntimeError("Neither Chrome nor Edge found on this machine.")

    print(f"Using browser: {browser}")
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--virtual-time-budget=5000",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Browser return code:", res.returncode)

    if os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"SUCCESS: Generated PDF at {pdf_path} ({size_kb:.1f} KB)")

        desktop_pdf = r"C:\Users\Bangk\Desktop\Assignment_4_2_Smart_Build_Cache_Invalidation_Bangkim_24BTRAO006.pdf"
        downloads_pdf = r"C:\Users\Bangk\Downloads\Assignment_4_2_Smart_Build_Cache_Invalidation_Bangkim_24BTRAO006.pdf"
        shutil.copyfile(pdf_path, desktop_pdf)
        shutil.copyfile(pdf_path, downloads_pdf)
        print(f"Copied to Desktop ({desktop_pdf}) and Downloads ({downloads_pdf}) successfully!")
    else:
        print("ERROR: PDF was not generated. Output:", res.stderr)

if __name__ == "__main__":
    generate_pdf()

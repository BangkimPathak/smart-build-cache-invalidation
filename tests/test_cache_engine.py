import os
import shutil
import tempfile
import pytest
from src.cache_engine import SmartCacheEngine
from src.utils import sha256_file


@pytest.fixture
def temp_workspace():
    """Sets up an isolated workspace for cache testing."""
    test_dir = tempfile.mkdtemp()
    cache_dir = os.path.join(test_dir, ".test_cache")
    src_dir = os.path.join(test_dir, "src")
    os.makedirs(src_dir, exist_ok=True)

    manifest = os.path.join(test_dir, "requirements.txt")
    with open(manifest, "w", encoding="utf-8") as f:
        f.write("pytest>=8.0.0\nrequests>=2.31.0\n")

    mod_a = os.path.join(src_dir, "module_a.py")
    with open(mod_a, "w", encoding="utf-8") as f:
        f.write("def func_a(): return 'A'\n")

    mod_b = os.path.join(src_dir, "module_b.py")
    with open(mod_b, "w", encoding="utf-8") as f:
        f.write("from module_a import func_a\ndef func_b(): return func_a() + 'B'\n")

    yield {
        "root": test_dir,
        "cache_dir": cache_dir,
        "src_dir": src_dir,
        "manifest": manifest,
        "mod_a": mod_a,
        "mod_b": mod_b
    }

    shutil.rmtree(test_dir, ignore_errors=True)


def test_deterministic_hashing(temp_workspace):
    """Verifies that normalized line endings produce identical hashes."""
    engine = SmartCacheEngine(cache_dir=temp_workspace["cache_dir"])
    h1 = engine.compute_manifest_hash(temp_workspace["manifest"])

    # Overwrite with CRLF line endings
    with open(temp_workspace["manifest"], "wb") as f:
        f.write(b"pytest>=8.0.0\r\nrequests>=2.31.0\r\n")
    h2 = engine.compute_manifest_hash(temp_workspace["manifest"])

    assert h1 == h2, "Hashing must be invariant to line ending differences"


def test_cache_miss_on_cold_build(temp_workspace):
    """Initial lookup on empty cache must report CACHE_MISS."""
    engine = SmartCacheEngine(cache_dir=temp_workspace["cache_dir"])
    pk, rks = engine.generate_cache_keys("test-build", temp_workspace["manifest"], temp_workspace["src_dir"])

    status, matched_key, _ = engine.lookup(pk, rks)
    assert status == "CACHE_MISS"
    assert matched_key is None


def test_exact_cache_hit_after_store(temp_workspace):
    """Subsequent lookup with identical files must report EXACT_HIT."""
    engine = SmartCacheEngine(cache_dir=temp_workspace["cache_dir"])
    pk, rks = engine.generate_cache_keys("test-build", temp_workspace["manifest"], temp_workspace["src_dir"])

    # Store build output
    engine.store(pk, {"status": "SUCCESS", "exit_code": 0})

    status, matched_key, metadata = engine.lookup(pk, rks)
    assert status == "EXACT_HIT"
    assert matched_key == pk
    assert metadata["data"]["exit_code"] == 0


def test_manifest_modification_invalidates_cache(temp_workspace):
    """Changing requirements.txt must invalidate the primary key and create a new hash."""
    engine = SmartCacheEngine(cache_dir=temp_workspace["cache_dir"])
    pk1, rks1 = engine.generate_cache_keys("test-build", temp_workspace["manifest"], temp_workspace["src_dir"])
    engine.store(pk1, {"cached": "v1"})

    # Modify requirements.txt (add a new dependency)
    with open(temp_workspace["manifest"], "a", encoding="utf-8") as f:
        f.write("pydantic>=2.0.0\n")

    pk2, rks2 = engine.generate_cache_keys("test-build", temp_workspace["manifest"], temp_workspace["src_dir"])
    assert pk1 != pk2, "Cache key must change when manifest is updated"

    # Lookup with new keys: should miss primary key
    status, matched_key, _ = engine.lookup(pk2, rks2)
    # Restore key 2 (prefix: os-py-prefix-) might match base, but primary key misses!
    assert matched_key != pk1 or status == "RESTORE_HIT"


def test_code_modification_allows_partial_restore_hit(temp_workspace):
    """When source code changes but dependencies remain unchanged, fallback restore-key hits."""
    engine = SmartCacheEngine(cache_dir=temp_workspace["cache_dir"])
    pk1, rks1 = engine.generate_cache_keys("test-build", temp_workspace["manifest"], temp_workspace["src_dir"])
    engine.store(pk1, {"built_wheels": ["wheel_a.whl", "wheel_b.whl"]})

    # Modify source code only
    with open(temp_workspace["mod_a"], "a", encoding="utf-8") as f:
        f.write("# comment\n")

    pk2, rks2 = engine.generate_cache_keys("test-build", temp_workspace["manifest"], temp_workspace["src_dir"])
    assert pk1 != pk2, "Primary key must change when source code changes"

    # Lookup should achieve RESTORE_HIT via rks2[0] (dependency match)
    status, matched_key, meta = engine.lookup(pk2, rks2)
    assert status == "RESTORE_HIT"
    assert matched_key == pk1
    assert "built_wheels" in meta["data"]


def test_dependency_graph_impact_analysis(temp_workspace):
    """
    Verifies that changing module_a correctly identifies module_a and module_b
    (which imports module_a) as impacted.
    """
    engine = SmartCacheEngine(cache_dir=temp_workspace["cache_dir"])
    impacted = engine.compute_impacted_modules([temp_workspace["mod_a"]], temp_workspace["src_dir"])

    assert "module_a" in impacted
    assert "module_b" in impacted

import ast
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from src.utils import sha256_file, sha256_bytes


class SmartCacheEngine:
    """
    Production-grade implementation of Content-Addressable Build Caching
    and Deterministic Cache Invalidation.

    Emulates GitHub Actions actions/cache@v4, Bazel, and TurboRepo mechanics:
    1. Cryptographic hashing of dependency manifests and source trees.
    2. Multi-tier key resolution (exact match vs. fallback restore-keys).
    3. AST-based dependency graph impact analysis for selective cache invalidation.
    """

    def __init__(self, cache_dir: str = ".smart_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "cache_index.json"
        self._load_index()

    def _load_index(self):
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except Exception:
                self.index = {}
        else:
            self.index = {}

    def _save_index(self):
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)

    def compute_manifest_hash(self, manifest_path: str) -> str:
        """Computes deterministic hash for dependency manifest (e.g. requirements.txt)."""
        return sha256_file(manifest_path)

    def compute_tree_hash(self, directory: str, pattern: str = "*.py") -> str:
        """
        Computes deterministic cumulative hash for all files matching pattern in directory.
        Sorts paths alphabetically to ensure reproducible hashing across platforms.
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            return "empty_tree"

        files = sorted(dir_path.rglob(pattern))
        if not files:
            return "empty_tree"

        hasher_input = []
        for file in files:
            rel_path = file.relative_to(dir_path).as_posix()
            file_hash = sha256_file(str(file))
            hasher_input.append(f"{rel_path}:{file_hash}")

        combined = "\n".join(hasher_input).encode("utf-8")
        return sha256_bytes(combined)

    def generate_cache_keys(
        self,
        prefix: str,
        manifest_path: str,
        src_dir: str,
        os_name: Optional[str] = None,
        py_version: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Generates deterministic primary key and hierarchical fallback restore-keys.

        Format:
        Primary Key:    {os}-{py}-{prefix}-{manifest_hash}-{src_hash}
        Restore-Key 1:  {os}-{py}-{prefix}-{manifest_hash}-
        Restore-Key 2:  {os}-{py}-{prefix}-
        """
        os_label = os_name or sys.platform
        py_label = py_version or f"py{sys.version_info.major}.{sys.version_info.minor}"

        dep_hash = self.compute_manifest_hash(manifest_path)
        src_hash = self.compute_tree_hash(src_dir)

        primary_key = f"{os_label}-{py_label}-{prefix}-{dep_hash}-{src_hash}"
        restore_keys = [
            f"{os_label}-{py_label}-{prefix}-{dep_hash}-",
            f"{os_label}-{py_label}-{prefix}-"
        ]

        return primary_key, restore_keys

    def lookup(self, primary_key: str, restore_keys: List[str]) -> Tuple[str, Optional[str], Optional[dict]]:
        """
        Performs multi-tier cache resolution.
        Returns:
            (status, matched_key, metadata)
            status can be: 'EXACT_HIT', 'RESTORE_HIT', or 'CACHE_MISS'
        """
        self._load_index()

        # 1. Check exact primary key
        if primary_key in self.index:
            entry = self.index[primary_key]
            return "EXACT_HIT", primary_key, entry

        # 2. Check fallback restore keys in order (prefix match)
        for rk in restore_keys:
            # Find the most recently stored entry matching the prefix
            matching_keys = [k for k in self.index if k.startswith(rk)]
            if matching_keys:
                # Pick the latest modified or highest timestamp
                best_match = max(matching_keys, key=lambda k: self.index[k].get("timestamp", 0))
                return "RESTORE_HIT", best_match, self.index[best_match]

        # 3. Cache Miss
        return "CACHE_MISS", None, None

    def store(self, key: str, data: dict, artifact_files: Optional[List[str]] = None):
        """Stores build metadata and copies artifacts into persistent cache."""
        import time

        key_dir = self.cache_dir / key
        key_dir.mkdir(parents=True, exist_ok=True)

        copied_artifacts = []
        if artifact_files:
            for art in artifact_files:
                p = Path(art)
                if p.exists():
                    dest = key_dir / p.name
                    if p.is_dir():
                        shutil.copytree(p, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(p, dest)
                    copied_artifacts.append(dest.name)

        self.index[key] = {
            "timestamp": time.time(),
            "data": data,
            "artifacts": copied_artifacts
        }
        self._save_index()

    def clear(self):
        """Clears all cached entries and the index."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.index = {}
            self._save_index()

    @staticmethod
    def extract_internal_imports(file_path: str) -> Set[str]:
        """Extracts locally imported module names using AST analysis."""
        imports = set()
        if not os.path.exists(file_path):
            return imports

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except Exception:
            pass
        return imports

    def compute_impacted_modules(self, changed_files: List[str], src_dir: str) -> Set[str]:
        """
        Builds a reverse dependency graph of all modules in src_dir and returns
        the complete set of modules that must be invalidated when changed_files are modified.
        """
        src_path = Path(src_dir)
        all_py = list(src_path.glob("*.py"))
        dep_graph: Dict[str, Set[str]] = {}

        # Build forward map: module -> imported_modules
        for py_file in all_py:
            mod_name = py_file.stem
            direct_imports = self.extract_internal_imports(str(py_file))
            # Keep only imports that exist in src
            internal = {imp.split(".")[-1] for imp in direct_imports if any(p.stem == imp.split(".")[-1] for p in all_py)}
            dep_graph[mod_name] = internal

        # Build reverse map: module -> modules that depend on it
        reverse_graph: Dict[str, Set[str]] = {m: set() for m in dep_graph}
        for mod, imports in dep_graph.items():
            for imp in imports:
                if imp in reverse_graph:
                    reverse_graph[imp].add(mod)

        # BFS / DFS to collect transitive impact
        impacted: Set[str] = set()
        to_visit = []
        for cf in changed_files:
            mod = Path(cf).stem
            if mod in dep_graph:
                impacted.add(mod)
                to_visit.append(mod)

        while to_visit:
            curr = to_visit.pop(0)
            for dependent in reverse_graph.get(curr, set()):
                if dependent not in impacted:
                    impacted.add(dependent)
                    to_visit.append(dependent)

        return impacted

import hashlib
import os
import time
from typing import List


def sha256_file(filepath: str) -> str:
    """Computes deterministic SHA-256 hash of a file normalized by line endings."""
    if not os.path.exists(filepath):
        return ""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        content = f.read().replace(b"\r\n", b"\n")
        hasher.update(content)
    return hasher.hexdigest()[:16]


def sha256_bytes(data: bytes) -> str:
    """Computes SHA-256 hash of raw byte payload."""
    return hashlib.sha256(data).hexdigest()[:16]


class Timer:
    """Context manager for accurate wall-clock timing."""
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start

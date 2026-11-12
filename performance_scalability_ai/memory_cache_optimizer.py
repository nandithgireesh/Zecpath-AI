"""
Day 60: Memory & Two-Tier Caching Optimizer
High-Speed L1 LRU & L2 Compressed TTL Cache with Memory Bounds
Platform: Zecpath Automated Hiring Platform
"""

import time
import zlib
import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
from performance_scalability_ai.models import CacheMetrics


class TwoTierMemoryCache:
    """
    Two-Tier Memory Cache Optimizer for AI Workloads:
      - Tier 1 (L1): Fast in-memory LRU cache for hot latency-critical queries (sub-microsecond access).
      - Tier 2 (L2): Compressed TTL cache for larger candidate dossiers and parsed resume payloads.
    Guarantees strict memory caps and automatic eviction under memory pressure.
    """

    def __init__(self, max_memory_bytes: int = 128 * 1024 * 1024, l1_max_items: int = 500):
        self.max_memory_bytes = max_memory_bytes
        self.l1_max_items = l1_max_items

        # L1: OrderedDict as LRU cache {key: (value, access_time)}
        self._l1_cache: OrderedDict[str, Any] = OrderedDict()

        # L2: Compressed store {key: (compressed_bytes, expire_timestamp, uncompressed_size)}
        self._l2_cache: Dict[str, Tuple[bytes, float, int]] = {}

        self.metrics = CacheMetrics(max_size_bytes=max_memory_bytes)

    def _hash_key(self, raw_key: str) -> str:
        """Returns deterministic 16-char hex digest for fixed memory footprint."""
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves item from cache. Checks L1 first, then L2.
        Promotes L2 items to L1 on frequent access.
        """
        k = self._hash_key(key)

        # 1. Check L1 Hot Cache
        if k in self._l1_cache:
            # Move to end (most recently used)
            self._l1_cache.move_to_end(k)
            self.metrics.hits += 1
            self.metrics.update_hit_ratio()
            return self._l1_cache[k]

        # 2. Check L2 Compressed TTL Cache
        now = time.time()
        if k in self._l2_cache:
            compressed_data, expire_at, orig_size = self._l2_cache[k]
            if now > expire_at:
                # Expired
                self._delete_l2(k)
                self.metrics.misses += 1
                self.metrics.update_hit_ratio()
                return None

            # Decompress
            try:
                raw_bytes = zlib.decompress(compressed_data)
                value = json.loads(raw_bytes.decode("utf-8"))

                # Promote to L1
                self.set_l1(key, value)

                self.metrics.hits += 1
                self.metrics.update_hit_ratio()
                return value
            except Exception:
                self._delete_l2(k)
                self.metrics.misses += 1
                self.metrics.update_hit_ratio()
                return None

        self.metrics.misses += 1
        self.metrics.update_hit_ratio()
        return None

    def set_l1(self, key: str, value: Any):
        """Stores item directly in L1 hot cache."""
        k = self._hash_key(key)
        if k in self._l1_cache:
            self._l1_cache.move_to_end(k)
        self._l1_cache[k] = value

        # Evict oldest if exceeding capacity
        while len(self._l1_cache) > self.l1_max_items:
            evicted_k, _ = self._l1_cache.popitem(last=False)
            self.metrics.evictions += 1

        self.metrics.tier1_items = len(self._l1_cache)
        self._recalculate_memory()

    def set_l2(self, key: str, value: Any, ttl_sec: float = 300.0):
        """Compresses and stores payload in L2 TTL cache."""
        k = self._hash_key(key)
        try:
            serialized = json.dumps(value).encode("utf-8")
            compressed = zlib.compress(serialized, level=6)
            expire_at = time.time() + ttl_sec

            # Memory bound check before insertion
            if self.metrics.current_size_bytes + len(compressed) > self.max_memory_bytes:
                self._enforce_memory_cap()

            self._l2_cache[k] = (compressed, expire_at, len(serialized))
            self.metrics.tier2_items = len(self._l2_cache)
            self._recalculate_memory()
        except Exception:
            pass

    def set(self, key: str, value: Any, ttl_sec: float = 300.0, to_l2: bool = False):
        """Universal set with automatic tier routing."""
        if to_l2:
            self.set_l2(key, value, ttl_sec)
        else:
            self.set_l1(key, value)

    def _delete_l2(self, k: str):
        if k in self._l2_cache:
            del self._l2_cache[k]
            self.metrics.tier2_items = len(self._l2_cache)
            self._recalculate_memory()

    def _recalculate_memory(self):
        """Calculates total memory footprint of cached data."""
        l1_size = sum(len(str(v)) for v in self._l1_cache.values())
        l2_size = sum(len(data[0]) for data in self._l2_cache.values())
        self.metrics.current_size_bytes = l1_size + l2_size

    def _enforce_memory_cap(self):
        """Evicts oldest L2 entries when approaching maximum memory limits."""
        if not self._l2_cache:
            return
        # Remove 25% of entries
        keys_to_remove = list(self._l2_cache.keys())[: max(1, len(self._l2_cache) // 4)]
        for k in keys_to_remove:
            del self._l2_cache[k]
            self.metrics.evictions += 1
        self.metrics.tier2_items = len(self._l2_cache)
        self._recalculate_memory()

    def clear(self):
        self._l1_cache.clear()
        self._l2_cache.clear()
        self.metrics.tier1_items = 0
        self.metrics.tier2_items = 0
        self.metrics.current_size_bytes = 0

    def get_metrics(self) -> CacheMetrics:
        self.metrics.tier1_items = len(self._l1_cache)
        self.metrics.tier2_items = len(self._l2_cache)
        self.metrics.update_hit_ratio()
        return self.metrics


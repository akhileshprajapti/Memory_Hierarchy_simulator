from .algorithms import CacheSet

VALID_POLICIES = {"LRU", "FIFO", "RANDOM"}
VALID_MAPPINGS = {"direct", "fully_associative", "set_associative"}

def parse_addresses(raw):
    if isinstance(raw, list):
        tokens = raw
    elif isinstance(raw, str):
        tokens = raw.replace(",", " ").replace("\n", " ").split()
    else:
        raise ValueError("Addresses must be entered as text or a list.")
    if not tokens:
        raise ValueError("Enter at least one memory address.")
    if len(tokens) > 500:
        raise ValueError("A maximum of 500 addresses is allowed.")
    addresses = []
    for token in tokens:
        try:
            value = int(str(token), 0)
        except ValueError:
            try:
                value = int(str(token), 10)
            except ValueError:
                raise ValueError(f"Invalid address: {token}")
        if value < 0:
            raise ValueError("Addresses cannot be negative.")
        addresses.append(value)
    return addresses

class CacheLevel:
    def __init__(self, name, size_kb, block_size, mapping, associativity, policy, access_time):
        self.name = name
        self.capacity_bytes = int(size_kb) * 1024
        self.block_size = block_size
        self.access_time = float(access_time)
        self.policy = policy
        if self.capacity_bytes <= 0 or self.capacity_bytes % block_size:
            raise ValueError(f"{name}: capacity must be positive and divisible by block size.")
        self.line_count = self.capacity_bytes // block_size
        if mapping == "direct":
            self.ways = 1
        elif mapping == "fully_associative":
            self.ways = self.line_count
        else:
            self.ways = int(associativity)
            if self.ways < 1 or self.line_count % self.ways:
                raise ValueError(f"{name}: associativity must divide the number of cache lines.")
        self.set_count = self.line_count // self.ways
        self.sets = [CacheSet(self.ways, policy) for _ in range(self.set_count)]
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def locate(self, address):
        block = address // self.block_size
        set_index = block % self.set_count
        tag = block // self.set_count
        return block, set_index, tag

    def access(self, address):
        block, set_index, tag = self.locate(address)
        hit, evicted = self.sets[set_index].access(tag)
        if hit:
            self.hits += 1
        else:
            self.misses += 1
            if evicted is not None:
                self.evictions += 1
        return {"hit": hit, "block": block, "set": set_index, "tag": tag, "evicted": evicted}

    def fill(self, address):
        _, set_index, tag = self.locate(address)
        self.sets[set_index].access(tag)

    def snapshot(self):
        return [
            {"set": i, "way": way, "tag": tag}
            for i, cache_set in enumerate(self.sets)
            for way, tag in enumerate(cache_set.blocks)
        ]

def _build_config(payload):
    addresses = parse_addresses(payload.get("addresses", "0, 16, 32, 0, 48, 16, 64, 0"))
    block_size = int(payload.get("block_size", 16))
    mapping = payload.get("mapping", "set_associative")
    associativity = int(payload.get("associativity", 2))
    policy = str(payload.get("replacement", "LRU")).upper()
    memory_penalty = float(payload.get("memory_penalty", 100))
    if block_size <= 0 or block_size & (block_size - 1):
        raise ValueError("Block size must be a positive power of two: 4, 8, 16, 32, 64.")
    if mapping not in VALID_MAPPINGS:
        raise ValueError("Select a valid mapping technique.")
    if policy not in VALID_POLICIES:
        raise ValueError("Select LRU, FIFO or Random.")
    if memory_penalty < 0:
        raise ValueError("Memory penalty cannot be negative.")

    raw_levels = payload.get("levels") or [
        {"name": "L1 Cache", "size_kb": 1, "access_time": 1, "enabled": True},
        {"name": "L2 Cache", "size_kb": 4, "access_time": 4, "enabled": True},
        {"name": "L3 Cache", "size_kb": 16, "access_time": 12, "enabled": True},
    ]
    levels = []
    for item in raw_levels:
        if item.get("enabled", True):
            size = int(item.get("size_kb", 1))
            time = float(item.get("access_time", 1))
            if time < 0:
                raise ValueError("Cache access time cannot be negative.")
            levels.append(CacheLevel(
                item.get("name", f"L{len(levels) + 1} Cache"), size,
                block_size, mapping, associativity, policy, time
            ))
    if not levels:
        raise ValueError("Enable at least one cache level.")
    return addresses, levels, memory_penalty, block_size, mapping, policy

def run_hierarchy(payload):
    addresses, levels, memory_penalty, block_size, mapping, policy = _build_config(payload)
    trace = []
    total_latency = 0.0
    main_memory_accesses = 0

    for step, address in enumerate(addresses, start=1):
        lookup = []
        latency = 0.0
        found_at = "Main Memory"

        for index, level in enumerate(levels):
            latency += level.access_time
            outcome = level.access(address)
            lookup.append({
                "level": level.name, "hit": outcome["hit"],
                "set": outcome["set"], "tag": outcome["tag"],
                "evicted": outcome["evicted"]
            })
            if outcome["hit"]:
                found_at = level.name
                for upper_level in levels[:index]:
                    upper_level.fill(address)
                break
        else:
            latency += memory_penalty
            main_memory_accesses += 1
            for level in levels:
                level.fill(address)

        total_latency += latency
        trace.append({
            "step": step, "address": address, "hex": hex(address),
            "found_at": found_at, "latency": round(latency, 3),
            "levels": lookup, "memory_access": found_at == "Main Memory"
        })

    total = len(addresses)
    l1_hits = sum(1 for item in trace if item["levels"] and item["levels"][0]["hit"])
    hierarchy_hits = total - main_memory_accesses
    level_stats = [{
        "name": level.name,
        "capacity_kb": round(level.capacity_bytes / 1024, 2),
        "access_time": level.access_time,
        "hits": level.hits,
        "misses": level.misses,
        "evictions": level.evictions,
        "hit_ratio": round(level.hits / max(1, level.hits + level.misses) * 100, 2),
        "miss_ratio": round(level.misses / max(1, level.hits + level.misses) * 100, 2),
        "lines": level.snapshot()
    } for level in levels]

    return {
        "configuration": {"mapping": mapping, "replacement": policy, "block_size": block_size},
        "summary": {
            "total_accesses": total,
            "l1_hits": l1_hits,
            "l1_misses": total - l1_hits,
            "memory_hits": hierarchy_hits,
            "memory_misses": main_memory_accesses,
            "hit_ratio": round(hierarchy_hits / total * 100, 2),
            "miss_ratio": round(main_memory_accesses / total * 100, 2),
            "amat": round(total_latency / total, 3),
            "total_latency": round(total_latency, 3),
            "main_memory_accesses": main_memory_accesses
        },
        "levels": level_stats,
        "trace": trace
    }

def compare_algorithms(payload):
    comparisons = []
    for policy in ("LRU", "FIFO", "RANDOM"):
        config = dict(payload)
        config["replacement"] = policy
        result = run_hierarchy(config)
        summary = result["summary"]
        comparisons.append({
            "algorithm": policy,
            "hit_ratio": summary["hit_ratio"],
            "miss_ratio": summary["miss_ratio"],
            "amat": summary["amat"],
            "main_memory_accesses": summary["main_memory_accesses"]
        })
    return comparisons

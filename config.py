DEFAULT_CONFIG = {
    "address_space": 65536,
    "block_size": 16,
    "memory_penalty": 100,
    "levels": [
        {"name": "L1 Cache", "size_kb": 1, "access_time": 1, "enabled": True},
        {"name": "L2 Cache", "size_kb": 4, "access_time": 4, "enabled": True},
        {"name": "L3 Cache", "size_kb": 16, "access_time": 12, "enabled": True},
    ],
    "mapping": "set_associative",
    "associativity": 2,
    "replacement": "LRU",
}

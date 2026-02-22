def merge_unique(items):
    seen = set()
    result = []

    for item in items:
        key = item.get("name", "").strip().lower()

        if key and key not in seen:
            seen.add(key)
            result.append(item)

    return result

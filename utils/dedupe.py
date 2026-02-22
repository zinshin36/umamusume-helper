def merge_unique(items):
    seen = {}
    for item in items:
        key = item["name"].strip().lower()
        if key not in seen:
            seen[key] = item
        else:
            # Merge missing data
            for k, v in item.items():
                if not seen[key].get(k) and v:
                    seen[key][k] = v
    return list(seen.values())

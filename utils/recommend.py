# Simple inheritance recommendation logic

INHERITANCE_PRIORITY = {
    "Short": ["Speed", "Power"],
    "Mile": ["Speed", "Power"],
    "Medium": ["Speed", "Stamina"],
    "Long": ["Stamina", "Power"]
}

def recommend_inheritance(horse_name, horses):
    """
    Recommend inheritance parents based on distance keywords in name
    """
    horse = next((h for h in horses if h["name"] == horse_name), None)
    if not horse:
        return "Horse not found."

    # Simple distance detection
    name_lower = horse_name.lower()

    if "long" in name_lower:
        distance = "Long"
    elif "medium" in name_lower:
        distance = "Medium"
    elif "mile" in name_lower:
        distance = "Mile"
    else:
        distance = "Short"

    stats = INHERITANCE_PRIORITY.get(distance, [])

    result = f"Inheritance Recommendation for {horse_name}\n"
    result += f"Primary Focus: {distance} distance\n\n"
    result += "Recommended Stats:\n"
    for stat in stats:
        result += f"- {stat}\n"

    result += "\nRecommended Parent Types:\n"
    result += "- Parents with matching distance aptitude\n"
    result += "- High star Speed/Stamina factors\n"
    result += "- Compatible racing strategy\n"

    return result

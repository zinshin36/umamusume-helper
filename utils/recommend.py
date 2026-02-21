import json

ARCHETYPE_FILE = "data/archetypes.json"

def load_archetypes():
    try:
        with open(ARCHETYPE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def recommend_inheritance(horse):
    archetypes = load_archetypes()

    archetype = "General"
    if horse["id"] in archetypes:
        archetype = archetypes[horse["id"]]["type"]

    return {
        "horse": horse["name"],
        "version": "Default",
        "recommended_skill": "Speed Boost",
        "archetype": archetype
    }

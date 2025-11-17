import json

def cargar_slots(json_file="../data/slots_basicos.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        slot_json = json.load(f)
    slots = slot_json["slots"]
    validation_functions = slot_json.get("validation_functions", {})
    return slots, validation_functions
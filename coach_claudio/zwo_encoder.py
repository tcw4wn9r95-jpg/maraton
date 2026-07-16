"""ZWO file encoder for TrainingPeaks/Zwift workout files.

Generates XML .zwo files from structured workout definitions.
Power values are expressed as fractions of FTP (1.0 = threshold).
"""

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

POWER_ZONES = {
    "recovery":  (0.55, 0.65),
    "easy":      (0.65, 0.76),
    "long":      (0.70, 0.78),
    "marathon":  (0.80, 0.88),
    "tempo":     (0.88, 0.95),
    "threshold": (0.95, 1.05),
    "interval":  (1.06, 1.20),
    "speed":     (1.20, 1.35),
    "strides":   (1.30, 1.50),
}


def _mid(zone: str) -> float:
    lo, hi = POWER_ZONES[zone]
    return round((lo + hi) / 2, 2)


def _lo(zone: str) -> float:
    return POWER_ZONES[zone][0]


def _hi(zone: str) -> float:
    return POWER_ZONES[zone][1]


def build_zwo(workout: dict) -> str:
    root = Element("workout_file")

    SubElement(root, "author").text = "Coach Claudio"
    SubElement(root, "name").text = workout["name"]
    SubElement(root, "description").text = workout.get("description", "")
    SubElement(root, "sportType").text = "run"

    tags_el = SubElement(root, "tags")
    SubElement(tags_el, "tag", name=workout.get("category", ""))
    SubElement(tags_el, "tag", name=workout.get("level", ""))

    wo = SubElement(root, "workout")

    for step in workout["steps"]:
        _add_step(wo, step)

    xml_str = tostring(root, encoding="unicode")
    return parseString(xml_str).toprettyxml(indent="    ", encoding=None)


def _add_step(parent: Element, step: dict):
    stype = step["type"]

    if stype == "warmup":
        zone = step.get("zone", "easy")
        SubElement(parent, "Warmup",
                   Duration=str(step["duration"]),
                   PowerLow=f"{_lo('recovery'):.2f}",
                   PowerHigh=f"{_hi(zone):.2f}")

    elif stype == "cooldown":
        zone = step.get("zone", "easy")
        SubElement(parent, "Cooldown",
                   Duration=str(step["duration"]),
                   PowerLow=f"{_hi(zone):.2f}",
                   PowerHigh=f"{_lo('recovery'):.2f}")

    elif stype == "steady":
        zone = step["zone"]
        lo, hi = POWER_ZONES[zone]
        el = SubElement(parent, "SteadyState",
                        Duration=str(step["duration"]),
                        Power=f"{_mid(zone):.2f}")
        if step.get("notes"):
            SubElement(el, "textevent",
                       timeoffset="0",
                       message=step["notes"])

    elif stype == "ramp":
        SubElement(parent, "Ramp",
                   Duration=str(step["duration"]),
                   PowerLow=f"{step['power_low']:.2f}",
                   PowerHigh=f"{step['power_high']:.2f}")

    elif stype == "intervals":
        on_zone = step["on_zone"]
        off_zone = step.get("off_zone", "recovery")
        SubElement(parent, "IntervalsT",
                   Repeat=str(step["reps"]),
                   OnDuration=str(step["on_duration"]),
                   OffDuration=str(step["off_duration"]),
                   OnPower=f"{_mid(on_zone):.2f}",
                   OffPower=f"{_mid(off_zone):.2f}")

    elif stype == "free":
        SubElement(parent, "FreeRide",
                   Duration=str(step["duration"]))

"""Coach Claudio Marathon Workout Library.

Comprehensive workout templates for marathon training across three levels:
beginner, intermediate, and advanced. Workouts are defined in a format-agnostic
way using zone names and durations in seconds, then exported to ZWO format.

Power zones are relative to FTP (1.0 = threshold), so levels differ by
volume (distance/reps/duration), not intensity percentages.
"""

# Reference paces (min/km) for estimating duration from distance
REFERENCE_PACES = {
    "beginner":     {"recovery": 7.75, "easy": 7.15, "long": 7.25, "marathon": 6.75,
                     "tempo": 6.35, "threshold": 6.0, "interval": 5.5, "speed": 5.0, "strides": 4.75},
    "intermediate": {"recovery": 6.5, "easy": 5.9, "long": 6.0, "marathon": 5.5,
                     "tempo": 5.1, "threshold": 4.8, "interval": 4.3, "speed": 3.9, "strides": 3.7},
    "advanced":     {"recovery": 5.75, "easy": 5.1, "long": 5.25, "marathon": 4.4,
                     "tempo": 4.3, "threshold": 4.05, "interval": 3.65, "speed": 3.3, "strides": 3.15},
}


def _km_to_sec(km, level, zone):
    pace = REFERENCE_PACES[level][zone]
    return int(km * pace * 60)


# ---------------------------------------------------------------------------
# Step builders
# ---------------------------------------------------------------------------

def warmup(duration_sec, zone="easy"):
    return {"type": "warmup", "duration": duration_sec, "zone": zone}


def cooldown(duration_sec, zone="easy"):
    return {"type": "cooldown", "duration": duration_sec, "zone": zone}


def steady(duration_sec, zone, notes=""):
    return {"type": "steady", "duration": duration_sec, "zone": zone, "notes": notes}


def intervals(reps, on_duration, off_duration, on_zone, off_zone="recovery"):
    return {"type": "intervals", "reps": reps, "on_duration": on_duration,
            "off_duration": off_duration, "on_zone": on_zone, "off_zone": off_zone}


def free(duration_sec):
    return {"type": "free", "duration": duration_sec}


def ramp(duration_sec, power_low, power_high):
    return {"type": "ramp", "duration": duration_sec,
            "power_low": power_low, "power_high": power_high}


# ---------------------------------------------------------------------------
# WORKOUT DEFINITIONS
# ---------------------------------------------------------------------------

def _easy_runs(level):
    distances = {"beginner": [5, 6, 7, 8], "intermediate": [8, 10, 12, 14], "advanced": [10, 12, 14, 16]}
    workouts = []
    for d in distances[level]:
        dur = _km_to_sec(d, level, "easy")
        workouts.append({
            "name": f"Easy Run {d}km",
            "category": "easy",
            "level": level,
            "description": "Steady easy-pace run. Conversational effort.",
            "steps": [steady(dur, "easy", "Relaxed, conversational pace")],
        })
    return workouts


def _recovery_runs(level):
    distances = {"beginner": [3, 4, 5], "intermediate": [5, 6, 8], "advanced": [6, 8, 10]}
    workouts = []
    for d in distances[level]:
        dur = _km_to_sec(d, level, "recovery")
        workouts.append({
            "name": f"Recovery Run {d}km",
            "category": "recovery",
            "level": level,
            "description": "Very easy effort to promote recovery.",
            "steps": [steady(dur, "recovery", "Very easy shuffle pace")],
        })
    return workouts


def _long_runs(level):
    distances = {
        "beginner":     [12, 14, 16, 18, 20, 22, 25, 28, 30, 32],
        "intermediate": [16, 18, 20, 22, 24, 26, 28, 30, 32, 35],
        "advanced":     [20, 22, 24, 26, 28, 30, 32, 34, 36, 38],
    }
    workouts = []
    for d in distances[level]:
        wu = _km_to_sec(2, level, "easy")
        main = _km_to_sec(d - 3, level, "long")
        cd = _km_to_sec(1, level, "easy")
        workouts.append({
            "name": f"Long Run {d}km",
            "category": "long_run",
            "level": level,
            "description": "Long aerobic run. Stay patient, fuel well.",
            "steps": [
                warmup(wu),
                steady(main, "long", "Steady long-run pace"),
                cooldown(cd),
            ],
        })
    return workouts


def _long_run_with_marathon_pace(level):
    configs = {
        "beginner":     [(20, 4), (24, 5), (28, 6)],
        "intermediate": [(24, 6), (28, 8), (32, 10)],
        "advanced":     [(28, 8), (32, 12), (36, 14)],
    }
    workouts = []
    for total_km, mp_km in configs[level]:
        easy_km = total_km - mp_km - 3
        workouts.append({
            "name": f"Long Run {total_km}km w/ {mp_km}km MP",
            "category": "long_run_mp",
            "level": level,
            "description": f"Long run finishing with {mp_km}km at marathon pace.",
            "steps": [
                warmup(_km_to_sec(2, level, "easy")),
                steady(_km_to_sec(easy_km, level, "long"), "long", "Easy long-run pace"),
                steady(_km_to_sec(mp_km, level, "marathon"), "marathon", "Marathon goal pace"),
                cooldown(_km_to_sec(1, level, "easy")),
            ],
        })
    return workouts


def _tempo_runs(level):
    configs = {
        "beginner":     [(15, 2), (20, 2), (25, 2)],
        "intermediate": [(20, 2), (25, 2), (30, 2), (35, 2)],
        "advanced":     [(25, 2), (30, 2), (35, 2), (40, 2)],
    }
    workouts = []
    for minutes_tempo, wu_cd_km in configs[level]:
        workouts.append({
            "name": f"Tempo Run {minutes_tempo}min",
            "category": "tempo",
            "level": level,
            "description": "Comfortably hard sustained effort.",
            "steps": [
                warmup(_km_to_sec(wu_cd_km, level, "easy")),
                steady(minutes_tempo * 60, "tempo", "Steady tempo effort"),
                cooldown(_km_to_sec(wu_cd_km, level, "easy")),
            ],
        })
    return workouts


def _cruise_intervals(level):
    configs = {
        "beginner":     [(3, 8, 2)],
        "intermediate": [(4, 8, 2), (3, 12, 2), (5, 8, 1.5)],
        "advanced":     [(4, 10, 1.5), (5, 10, 1), (3, 15, 1.5)],
    }
    workouts = []
    for reps, min_on, min_off in configs[level]:
        workouts.append({
            "name": f"Cruise Intervals {reps}x{min_on}min",
            "category": "cruise_intervals",
            "level": level,
            "description": "Tempo pace broken into segments with short rest.",
            "steps": [
                warmup(600),
                intervals(reps, min_on * 60, int(min_off * 60), "tempo", "recovery"),
                cooldown(600),
            ],
        })
    return workouts


def _threshold_intervals(level):
    configs = {
        "beginner":     [(4, 1000, 400), (5, 800, 400)],
        "intermediate": [(5, 1000, 400), (4, 1600, 400), (6, 1000, 200)],
        "advanced":     [(6, 1000, 200), (5, 1600, 400), (4, 2000, 400), (8, 1000, 200)],
    }
    workouts = []
    for reps, dist_m, rest_m in configs[level]:
        on_dur = _km_to_sec(dist_m / 1000, level, "threshold")
        off_dur = _km_to_sec(rest_m / 1000, level, "recovery")
        dist_label = f"{dist_m}m" if dist_m < 1000 else f"{dist_m/1000:.1f}km"
        workouts.append({
            "name": f"Threshold {reps}x{dist_label}",
            "category": "threshold",
            "level": level,
            "description": "Hard but controlled. Just below race 10K effort.",
            "steps": [
                warmup(_km_to_sec(2, level, "easy")),
                intervals(reps, on_dur, off_dur, "threshold", "recovery"),
                cooldown(_km_to_sec(2, level, "easy")),
            ],
        })
    return workouts


def _vo2max_intervals(level):
    configs = {
        "beginner":     [(5, 600, 400), (6, 400, 400)],
        "intermediate": [(6, 800, 400), (8, 600, 300), (5, 1000, 400)],
        "advanced":     [(8, 800, 400), (6, 1000, 400), (10, 600, 200), (5, 1200, 400)],
    }
    workouts = []
    for reps, dist_m, rest_m in configs[level]:
        on_dur = _km_to_sec(dist_m / 1000, level, "interval")
        off_dur = _km_to_sec(rest_m / 1000, level, "recovery")
        workouts.append({
            "name": f"VO2max {reps}x{dist_m}m",
            "category": "vo2max",
            "level": level,
            "description": "Fast intervals at 3K-5K effort. Build top-end aerobic power.",
            "steps": [
                warmup(_km_to_sec(2, level, "easy")),
                intervals(reps, on_dur, off_dur, "interval", "recovery"),
                cooldown(_km_to_sec(2, level, "easy")),
            ],
        })
    return workouts


def _speed_intervals(level):
    configs = {
        "beginner":     [(6, 200, 200), (8, 150, 200)],
        "intermediate": [(8, 200, 200), (10, 200, 200), (6, 300, 300)],
        "advanced":     [(10, 200, 200), (8, 300, 200), (12, 200, 100), (6, 400, 200)],
    }
    workouts = []
    for reps, dist_m, rest_m in configs[level]:
        on_dur = _km_to_sec(dist_m / 1000, level, "speed")
        off_dur = _km_to_sec(rest_m / 1000, level, "recovery")
        workouts.append({
            "name": f"Speed Reps {reps}x{dist_m}m",
            "category": "speed",
            "level": level,
            "description": "Fast, relaxed strides. Focus on form.",
            "steps": [
                warmup(_km_to_sec(2, level, "easy")),
                intervals(reps, on_dur, off_dur, "speed", "recovery"),
                cooldown(_km_to_sec(2, level, "easy")),
            ],
        })
    return workouts


def _hill_repeats(level):
    configs = {
        "beginner":     [(4, 60, 90), (6, 45, 60)],
        "intermediate": [(6, 60, 90), (8, 45, 60), (4, 90, 120)],
        "advanced":     [(8, 60, 90), (10, 45, 60), (6, 90, 120), (5, 120, 150)],
    }
    workouts = []
    for reps, sec_up, sec_down in configs[level]:
        workouts.append({
            "name": f"Hill Repeats {reps}x{sec_up}s",
            "category": "hills",
            "level": level,
            "description": "Hard uphill, easy jog down. Builds strength and power.",
            "steps": [
                warmup(600),
                intervals(reps, sec_up, sec_down, "threshold", "recovery"),
                cooldown(600),
            ],
        })
    return workouts


def _fartlek(level):
    configs = {
        "beginner":     [
            ("Fartlek 6x2min", 6, 120, 120),
            ("Fartlek 8x1min", 8, 60, 90),
        ],
        "intermediate": [
            ("Fartlek 8x2min", 8, 120, 90),
            ("Fartlek 6x3min", 6, 180, 120),
            ("Fartlek Ladder 1-2-3-2-1", 5, 120, 90),
        ],
        "advanced":     [
            ("Fartlek 10x2min", 10, 120, 60),
            ("Fartlek 8x3min", 8, 180, 90),
            ("Fartlek 6x4min", 6, 240, 120),
            ("Fartlek 12x1min", 12, 60, 60),
        ],
    }
    workouts = []
    for name, reps, sec_on, sec_off in configs[level]:
        workouts.append({
            "name": name,
            "category": "fartlek",
            "level": level,
            "description": "Unstructured speed play. Fun and fast.",
            "steps": [
                warmup(600),
                intervals(reps, sec_on, sec_off, "threshold", "easy"),
                cooldown(600),
            ],
        })
    return workouts


def _marathon_pace_runs(level):
    distances = {
        "beginner":     [6, 8, 10, 12],
        "intermediate": [10, 12, 14, 16, 18],
        "advanced":     [14, 16, 18, 20, 22],
    }
    workouts = []
    for mp_km in distances[level]:
        workouts.append({
            "name": f"Marathon Pace {mp_km}km",
            "category": "marathon_pace",
            "level": level,
            "description": "Practice race pace. Dial in fueling strategy.",
            "steps": [
                warmup(_km_to_sec(2, level, "easy")),
                steady(_km_to_sec(mp_km, level, "marathon"), "marathon", "Marathon goal pace"),
                cooldown(_km_to_sec(2, level, "easy")),
            ],
        })
    return workouts


def _progression_runs(level):
    distances = {
        "beginner":     [8, 10],
        "intermediate": [10, 12, 14],
        "advanced":     [12, 14, 16, 18],
    }
    workouts = []
    for total_km in distances[level]:
        third = total_km / 3
        workouts.append({
            "name": f"Progression Run {total_km}km",
            "category": "progression",
            "level": level,
            "description": "Start easy, finish fast. Teaches pacing discipline.",
            "steps": [
                steady(_km_to_sec(third, level, "easy"), "easy", "Easy pace - first third"),
                steady(_km_to_sec(third, level, "marathon"), "marathon", "Marathon pace - middle third"),
                steady(_km_to_sec(third, level, "tempo"), "tempo", "Tempo pace - final push"),
            ],
        })
    return workouts


def _easy_with_strides(level):
    configs = {
        "beginner":     [(5, 4), (6, 6)],
        "intermediate": [(8, 6), (10, 8)],
        "advanced":     [(10, 8), (12, 10)],
    }
    workouts = []
    for run_km, num_strides in configs[level]:
        workouts.append({
            "name": f"Easy {run_km}km + {num_strides} Strides",
            "category": "easy_strides",
            "level": level,
            "description": "Easy run with finishing strides to maintain turnover.",
            "steps": [
                steady(_km_to_sec(run_km, level, "easy"), "easy", "Easy pace"),
                intervals(num_strides, 20, 40, "strides", "recovery"),
            ],
        })
    return workouts


def _race_simulation(level):
    configs = {
        "beginner":     [(15, "Half Marathon Simulation")],
        "intermediate": [(21, "Half Marathon Race Sim"), (30, "30km Race Sim")],
        "advanced":     [(21, "Half Marathon Time Trial"), (30, "30km Dress Rehearsal"), (35, "35km Race Sim")],
    }
    workouts = []
    for total_km, name in configs[level]:
        workouts.append({
            "name": name,
            "category": "race_simulation",
            "level": level,
            "description": "Full dress rehearsal. Practice everything: pace, fueling, gear.",
            "steps": [
                warmup(_km_to_sec(2, level, "easy")),
                steady(_km_to_sec(total_km - 3, level, "marathon"), "marathon", "Marathon race pace"),
                cooldown(_km_to_sec(1, level, "easy")),
            ],
        })
    return workouts


def _yasso_800s(level):
    reps_list = {"beginner": [4, 6], "intermediate": [6, 8, 10], "advanced": [8, 10, 12]}
    workouts = []
    for reps in reps_list[level]:
        on_dur = _km_to_sec(0.8, level, "interval")
        off_dur = on_dur  # Yasso: equal work and rest
        workouts.append({
            "name": f"Yasso 800s x{reps}",
            "category": "yasso",
            "level": level,
            "description": "Classic marathon predictor. 800m reps with equal rest.",
            "steps": [
                warmup(_km_to_sec(2, level, "easy")),
                intervals(reps, on_dur, off_dur, "interval", "recovery"),
                cooldown(_km_to_sec(2, level, "easy")),
            ],
        })
    return workouts


def _pre_race_shakeout(level):
    distances = {"beginner": 3, "intermediate": 4, "advanced": 5}
    km = distances[level]
    return [{
        "name": "Pre-Race Shakeout",
        "category": "shakeout",
        "level": level,
        "description": "Day-before-race loosener. Short and easy with a few openers.",
        "steps": [
            steady(_km_to_sec(km, level, "easy"), "easy", "Very easy jog"),
            intervals(4, 20, 40, "strides", "recovery"),
        ],
    }]


# ---------------------------------------------------------------------------
# Library assembly
# ---------------------------------------------------------------------------

GENERATORS = [
    _easy_runs,
    _recovery_runs,
    _long_runs,
    _long_run_with_marathon_pace,
    _tempo_runs,
    _cruise_intervals,
    _threshold_intervals,
    _vo2max_intervals,
    _speed_intervals,
    _hill_repeats,
    _fartlek,
    _marathon_pace_runs,
    _progression_runs,
    _easy_with_strides,
    _race_simulation,
    _yasso_800s,
    _pre_race_shakeout,
]

LEVELS = ["beginner", "intermediate", "advanced"]


def build_library() -> list[dict]:
    library = []
    for gen in GENERATORS:
        for level in LEVELS:
            library.extend(gen(level))
    return library


def get_by_category(category: str) -> list[dict]:
    return [w for w in build_library() if w["category"] == category]


def get_by_level(level: str) -> list[dict]:
    return [w for w in build_library() if w["level"] == level]


def get_categories() -> list[str]:
    return sorted(set(w["category"] for w in build_library()))

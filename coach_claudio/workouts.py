"""Coach Claudio Marathon Workout Library.

Comprehensive workout templates for marathon training across three levels:
beginner, intermediate, and advanced. Each workout is defined with structured
steps that map directly to TrainingPeaks/Garmin workout step format.

Paces are defined in m/s (FIT standard). Helper functions convert from min/km.
Heart rate zones follow the 5-zone model (% of max HR).
"""

from coach_claudio.fit_encoder import (
    DURATION_TIME,
    DURATION_DISTANCE,
    DURATION_OPEN,
    DURATION_REPEAT_UNTIL_STEPS_COMPLETE,
    TARGET_SPEED,
    TARGET_HEART_RATE,
    TARGET_OPEN,
    INTENSITY_ACTIVE,
    INTENSITY_REST,
    INTENSITY_WARMUP,
    INTENSITY_COOLDOWN,
)


def pace_to_speed(min_per_km: float) -> float:
    """Convert min/km pace to m/s speed."""
    return 1000.0 / (min_per_km * 60.0)


def speed_to_fit(speed_mps: float) -> int:
    """Convert m/s to FIT speed format (mm/s as uint32)."""
    return int(speed_mps * 1000)


def pace_range(slow_min_km: float, fast_min_km: float) -> tuple[int, int]:
    """Return (low_speed, high_speed) in FIT mm/s from pace range.
    Note: slower pace = lower speed, faster pace = higher speed.
    """
    return speed_to_fit(pace_to_speed(slow_min_km)), speed_to_fit(pace_to_speed(fast_min_km))


def hr_range(low_pct: int, high_pct: int) -> tuple[int, int]:
    """HR target as % of max. FIT uses bpm offset by 100 for zone-based."""
    return 100 + low_pct, 100 + high_pct


def time_seconds(minutes: float) -> int:
    return int(minutes * 60 * 1000)  # FIT uses milliseconds


def distance_meters(km: float) -> int:
    return int(km * 100000)  # FIT uses centimeters (100ths of meter)


def step(duration_type, duration_value, target_type, target_value,
         target_low, target_high, intensity, notes=""):
    return {
        "duration_type": duration_type,
        "duration_value": duration_value,
        "target_type": target_type,
        "target_value": target_value,
        "target_low": target_low,
        "target_high": target_high,
        "intensity": intensity,
        "notes": notes,
    }


def warmup_time(minutes, hr_low=60, hr_high=75):
    lo, hi = hr_range(hr_low, hr_high)
    return step(DURATION_TIME, time_seconds(minutes),
                TARGET_HEART_RATE, 0, lo, hi, INTENSITY_WARMUP,
                "Easy warmup jog")


def cooldown_time(minutes, hr_low=55, hr_high=70):
    lo, hi = hr_range(hr_low, hr_high)
    return step(DURATION_TIME, time_seconds(minutes),
                TARGET_HEART_RATE, 0, lo, hi, INTENSITY_COOLDOWN,
                "Easy cooldown jog")


def warmup_dist(km, hr_low=60, hr_high=75):
    lo, hi = hr_range(hr_low, hr_high)
    return step(DURATION_DISTANCE, distance_meters(km),
                TARGET_HEART_RATE, 0, lo, hi, INTENSITY_WARMUP,
                "Easy warmup jog")


def cooldown_dist(km, hr_low=55, hr_high=70):
    lo, hi = hr_range(hr_low, hr_high)
    return step(DURATION_DISTANCE, distance_meters(km),
                TARGET_HEART_RATE, 0, lo, hi, INTENSITY_COOLDOWN,
                "Easy cooldown jog")


def repeat_step(back_to_step, repeat_count):
    return step(DURATION_REPEAT_UNTIL_STEPS_COMPLETE, back_to_step,
                TARGET_OPEN, repeat_count, 0, 0, INTENSITY_ACTIVE)


# ---------------------------------------------------------------------------
# Pace tables (min/km) by level
# ---------------------------------------------------------------------------

PACES = {
    "beginner": {
        "easy":      (7.00, 7.30),
        "long":      (7.00, 7.45),
        "recovery":  (7.30, 8.00),
        "tempo":     (6.15, 6.30),
        "threshold": (5.50, 6.10),
        "interval":  (5.20, 5.40),
        "speed":     (4.50, 5.10),
        "marathon":  (6.30, 7.00),
        "strides":   (4.30, 5.00),
    },
    "intermediate": {
        "easy":      (5.40, 6.10),
        "long":      (5.45, 6.20),
        "recovery":  (6.15, 6.45),
        "tempo":     (5.00, 5.15),
        "threshold": (4.40, 5.00),
        "interval":  (4.10, 4.30),
        "speed":     (3.45, 4.05),
        "marathon":  (5.15, 5.40),
        "strides":   (3.30, 3.50),
    },
    "advanced": {
        "easy":      (4.50, 5.20),
        "long":      (5.00, 5.30),
        "recovery":  (5.30, 6.00),
        "tempo":     (4.10, 4.25),
        "threshold": (3.55, 4.10),
        "interval":  (3.30, 3.50),
        "speed":     (3.10, 3.30),
        "marathon":  (4.15, 4.30),
        "strides":   (3.00, 3.20),
    },
}


def _p(level, zone):
    slow, fast = PACES[level][zone]
    return pace_range(slow, fast)


# ---------------------------------------------------------------------------
# WORKOUT DEFINITIONS
# ---------------------------------------------------------------------------

def _easy_runs(level):
    """Easy aerobic runs at various distances."""
    distances = {
        "beginner":     [5, 6, 7, 8],
        "intermediate": [8, 10, 12, 14],
        "advanced":     [10, 12, 14, 16],
    }
    workouts = []
    for d in distances[level]:
        lo, hi = _p(level, "easy")
        workouts.append({
            "name": f"Easy Run {d}km",
            "category": "easy",
            "level": level,
            "description": f"Steady easy-pace run. Conversational effort.",
            "steps": [
                step(DURATION_DISTANCE, distance_meters(d),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Relaxed, conversational pace"),
            ],
        })
    return workouts


def _recovery_runs(level):
    """Very easy recovery runs."""
    distances = {
        "beginner":     [3, 4, 5],
        "intermediate": [5, 6, 8],
        "advanced":     [6, 8, 10],
    }
    workouts = []
    for d in distances[level]:
        lo, hi = _p(level, "recovery")
        workouts.append({
            "name": f"Recovery Run {d}km",
            "category": "recovery",
            "level": level,
            "description": f"Very easy effort to promote recovery.",
            "steps": [
                step(DURATION_DISTANCE, distance_meters(d),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Very easy, shuffle pace"),
            ],
        })
    return workouts


def _long_runs(level):
    """Progressive long runs — the backbone of marathon prep."""
    configs = {
        "beginner":     [12, 14, 16, 18, 20, 22, 25, 28, 30, 32],
        "intermediate": [16, 18, 20, 22, 24, 26, 28, 30, 32, 35],
        "advanced":     [20, 22, 24, 26, 28, 30, 32, 34, 36, 38],
    }
    workouts = []
    for d in configs[level]:
        lo, hi = _p(level, "long")
        workouts.append({
            "name": f"Long Run {d}km",
            "category": "long_run",
            "level": level,
            "description": f"Long aerobic run. Stay patient, fuel well.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(d - 3),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Steady long-run pace"),
                cooldown_dist(1),
            ],
        })
    return workouts


def _long_run_with_marathon_pace(level):
    """Long runs finishing at marathon pace."""
    configs = {
        "beginner":     [(20, 4), (24, 5), (28, 6)],
        "intermediate": [(24, 6), (28, 8), (32, 10)],
        "advanced":     [(28, 8), (32, 12), (36, 14)],
    }
    workouts = []
    for total_km, mp_km in configs[level]:
        lo_long, hi_long = _p(level, "long")
        lo_mp, hi_mp = _p(level, "marathon")
        easy_km = total_km - mp_km - 3
        workouts.append({
            "name": f"Long Run {total_km}km w/ {mp_km}km MP",
            "category": "long_run_mp",
            "level": level,
            "description": f"Long run finishing with {mp_km}km at marathon pace.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(easy_km),
                     TARGET_SPEED, 0, lo_long, hi_long, INTENSITY_ACTIVE,
                     "Easy long-run pace"),
                step(DURATION_DISTANCE, distance_meters(mp_km),
                     TARGET_SPEED, 0, lo_mp, hi_mp, INTENSITY_ACTIVE,
                     "Marathon goal pace"),
                cooldown_dist(1),
            ],
        })
    return workouts


def _tempo_runs(level):
    """Sustained tempo efforts."""
    configs = {
        "beginner":     [(15, 3), (20, 4), (25, 5)],
        "intermediate": [(20, 5), (25, 6), (30, 8), (35, 10)],
        "advanced":     [(25, 8), (30, 10), (35, 12), (40, 15)],
    }
    workouts = []
    for minutes_tempo, warmup_cd_km in configs[level]:
        lo, hi = _p(level, "tempo")
        workouts.append({
            "name": f"Tempo Run {minutes_tempo}min",
            "category": "tempo",
            "level": level,
            "description": f"Comfortably hard sustained effort.",
            "steps": [
                warmup_dist(warmup_cd_km / 2),
                step(DURATION_TIME, time_seconds(minutes_tempo),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Steady tempo effort"),
                cooldown_dist(warmup_cd_km / 2),
            ],
        })
    return workouts


def _cruise_intervals(level):
    """Tempo broken into intervals with short recovery."""
    configs = {
        "beginner":     [(3, 8, 2)],
        "intermediate": [(4, 8, 2), (3, 12, 2), (5, 8, 1.5)],
        "advanced":     [(4, 10, 1.5), (5, 10, 1), (3, 15, 1.5)],
    }
    workouts = []
    for reps, minutes_on, minutes_rest in configs[level]:
        lo, hi = _p(level, "tempo")
        workouts.append({
            "name": f"Cruise Intervals {reps}x{minutes_on}min",
            "category": "cruise_intervals",
            "level": level,
            "description": f"Tempo pace broken into segments with short rest.",
            "steps": [
                warmup_time(10),
                step(DURATION_TIME, time_seconds(minutes_on),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Tempo pace"),
                step(DURATION_TIME, time_seconds(minutes_rest),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Easy jog recovery"),
                repeat_step(1, reps),
                cooldown_time(10),
            ],
        })
    return workouts


def _threshold_intervals(level):
    """Lactate threshold intervals."""
    configs = {
        "beginner":     [(4, 1000, 400), (5, 800, 400)],
        "intermediate": [(5, 1000, 400), (4, 1600, 400), (6, 1000, 200)],
        "advanced":     [(6, 1000, 200), (5, 1600, 400), (4, 2000, 400), (8, 1000, 200)],
    }
    workouts = []
    for reps, dist_m, rest_m in configs[level]:
        lo, hi = _p(level, "threshold")
        dist_label = f"{dist_m}m" if dist_m < 1000 else f"{dist_m/1000:.1f}km"
        workouts.append({
            "name": f"Threshold {reps}x{dist_label}",
            "category": "threshold",
            "level": level,
            "description": f"Hard but controlled. Just below race 10K effort.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(dist_m / 1000),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Threshold pace"),
                step(DURATION_DISTANCE, distance_meters(rest_m / 1000),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Jog recovery"),
                repeat_step(1, reps),
                cooldown_dist(2),
            ],
        })
    return workouts


def _vo2max_intervals(level):
    """Short fast intervals to build VO2max."""
    configs = {
        "beginner":     [(5, 600, 400), (6, 400, 400)],
        "intermediate": [(6, 800, 400), (8, 600, 300), (5, 1000, 400)],
        "advanced":     [(8, 800, 400), (6, 1000, 400), (10, 600, 200), (5, 1200, 400)],
    }
    workouts = []
    for reps, dist_m, rest_m in configs[level]:
        lo, hi = _p(level, "interval")
        dist_label = f"{dist_m}m"
        workouts.append({
            "name": f"VO2max {reps}x{dist_label}",
            "category": "vo2max",
            "level": level,
            "description": f"Fast intervals at 3K-5K effort. Build top-end aerobic power.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(dist_m / 1000),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Hard effort, controlled"),
                step(DURATION_DISTANCE, distance_meters(rest_m / 1000),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Jog recovery"),
                repeat_step(1, reps),
                cooldown_dist(2),
            ],
        })
    return workouts


def _speed_intervals(level):
    """Short speed reps for neuromuscular power."""
    configs = {
        "beginner":     [(6, 200, 200), (8, 150, 200)],
        "intermediate": [(8, 200, 200), (10, 200, 200), (6, 300, 300)],
        "advanced":     [(10, 200, 200), (8, 300, 200), (12, 200, 100), (6, 400, 200)],
    }
    workouts = []
    for reps, dist_m, rest_m in configs[level]:
        lo, hi = _p(level, "speed")
        workouts.append({
            "name": f"Speed Reps {reps}x{dist_m}m",
            "category": "speed",
            "level": level,
            "description": f"Fast, relaxed strides. Focus on form.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(dist_m / 1000),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Fast and smooth"),
                step(DURATION_DISTANCE, distance_meters(rest_m / 1000),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Walk/jog recovery"),
                repeat_step(1, reps),
                cooldown_dist(2),
            ],
        })
    return workouts


def _hill_repeats(level):
    """Hill repeat workouts."""
    configs = {
        "beginner":     [(4, 1.0, 1.5), (6, 0.75, 1.0)],
        "intermediate": [(6, 1.0, 1.5), (8, 0.75, 1.0), (4, 1.5, 2.0)],
        "advanced":     [(8, 1.0, 1.5), (10, 0.75, 1.0), (6, 1.5, 2.0), (5, 2.0, 2.5)],
    }
    workouts = []
    for reps, min_up, min_down in configs[level]:
        workouts.append({
            "name": f"Hill Repeats {reps}x{min_up}min",
            "category": "hills",
            "level": level,
            "description": f"Hard uphill, easy jog down. Builds strength and power.",
            "steps": [
                warmup_time(10),
                step(DURATION_TIME, time_seconds(min_up),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_ACTIVE,
                     "Hard uphill effort"),
                step(DURATION_TIME, time_seconds(min_down),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Easy jog downhill"),
                repeat_step(1, reps),
                cooldown_time(10),
            ],
        })
    return workouts


def _fartlek(level):
    """Fartlek (speed play) workouts with varied pace changes."""
    configs = {
        "beginner":     [
            ("Fartlek 6x2min", 6, 2.0, 2.0),
            ("Fartlek 8x1min", 8, 1.0, 1.5),
        ],
        "intermediate": [
            ("Fartlek 8x2min", 8, 2.0, 1.5),
            ("Fartlek 6x3min", 6, 3.0, 2.0),
            ("Fartlek Ladder 1-2-3-2-1", 5, 2.0, 1.5),
        ],
        "advanced":     [
            ("Fartlek 10x2min", 10, 2.0, 1.0),
            ("Fartlek 8x3min", 8, 3.0, 1.5),
            ("Fartlek 6x4min", 6, 4.0, 2.0),
            ("Fartlek 12x1min", 12, 1.0, 1.0),
        ],
    }
    workouts = []
    for name, reps, min_on, min_off in configs[level]:
        lo, hi = _p(level, "threshold")
        workouts.append({
            "name": name,
            "category": "fartlek",
            "level": level,
            "description": "Unstructured speed play. Fun and fast.",
            "steps": [
                warmup_time(10),
                step(DURATION_TIME, time_seconds(min_on),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Pick it up - hard effort"),
                step(DURATION_TIME, time_seconds(min_off),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Easy jog"),
                repeat_step(1, reps),
                cooldown_time(10),
            ],
        })
    return workouts


def _marathon_pace_runs(level):
    """Dedicated marathon-pace workouts."""
    configs = {
        "beginner":     [6, 8, 10, 12],
        "intermediate": [10, 12, 14, 16, 18],
        "advanced":     [14, 16, 18, 20, 22],
    }
    workouts = []
    for mp_km in configs[level]:
        lo, hi = _p(level, "marathon")
        workouts.append({
            "name": f"Marathon Pace {mp_km}km",
            "category": "marathon_pace",
            "level": level,
            "description": f"Practice race pace. Dial in fueling strategy.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(mp_km),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Marathon goal pace"),
                cooldown_dist(2),
            ],
        })
    return workouts


def _progression_runs(level):
    """Runs that get progressively faster."""
    configs = {
        "beginner":     [(8,), (10,)],
        "intermediate": [(10,), (12,), (14,)],
        "advanced":     [(12,), (14,), (16,), (18,)],
    }
    workouts = []
    for (total_km,) in configs[level]:
        lo_easy, hi_easy = _p(level, "easy")
        lo_tempo, hi_tempo = _p(level, "tempo")
        lo_mp, hi_mp = _p(level, "marathon")
        third = total_km / 3
        workouts.append({
            "name": f"Progression Run {total_km}km",
            "category": "progression",
            "level": level,
            "description": f"Start easy, finish fast. Teaches pacing discipline.",
            "steps": [
                step(DURATION_DISTANCE, distance_meters(third),
                     TARGET_SPEED, 0, lo_easy, hi_easy, INTENSITY_WARMUP,
                     "Easy pace - first third"),
                step(DURATION_DISTANCE, distance_meters(third),
                     TARGET_SPEED, 0, lo_mp, hi_mp, INTENSITY_ACTIVE,
                     "Marathon pace - middle third"),
                step(DURATION_DISTANCE, distance_meters(third),
                     TARGET_SPEED, 0, lo_tempo, hi_tempo, INTENSITY_ACTIVE,
                     "Tempo pace - final push"),
            ],
        })
    return workouts


def _easy_with_strides(level):
    """Easy run finishing with strides."""
    configs = {
        "beginner":     [(5, 4), (6, 6)],
        "intermediate": [(8, 6), (10, 8)],
        "advanced":     [(10, 8), (12, 10)],
    }
    workouts = []
    for run_km, num_strides in configs[level]:
        lo, hi = _p(level, "easy")
        lo_s, hi_s = _p(level, "strides")
        workouts.append({
            "name": f"Easy {run_km}km + {num_strides} Strides",
            "category": "easy_strides",
            "level": level,
            "description": f"Easy run with finishing strides to maintain turnover.",
            "steps": [
                step(DURATION_DISTANCE, distance_meters(run_km),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "Easy pace"),
                step(DURATION_DISTANCE, distance_meters(0.1),
                     TARGET_SPEED, 0, lo_s, hi_s, INTENSITY_ACTIVE,
                     "Stride: fast and relaxed"),
                step(DURATION_DISTANCE, distance_meters(0.1),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Walk back recovery"),
                repeat_step(1, num_strides),
            ],
        })
    return workouts


def _race_simulation(level):
    """Full race dress rehearsal workouts."""
    configs = {
        "beginner":     [(15, "Half Marathon Simulation")],
        "intermediate": [(21, "Half Marathon Race Sim"), (30, "30km Race Sim")],
        "advanced":     [(21, "Half Marathon Time Trial"), (30, "30km Dress Rehearsal"), (35, "35km Race Sim")],
    }
    workouts = []
    for total_km, name in configs[level]:
        lo_mp, hi_mp = _p(level, "marathon")
        workouts.append({
            "name": name,
            "category": "race_simulation",
            "level": level,
            "description": f"Full dress rehearsal. Practice everything: pace, fueling, gear.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(total_km - 3),
                     TARGET_SPEED, 0, lo_mp, hi_mp, INTENSITY_ACTIVE,
                     "Marathon race pace - race day simulation"),
                cooldown_dist(1),
            ],
        })
    return workouts


def _yasso_800s(level):
    """Yasso 800s - classic marathon predictor workout."""
    configs = {
        "beginner":     [4, 6],
        "intermediate": [6, 8, 10],
        "advanced":     [8, 10, 12],
    }
    workouts = []
    for reps in configs[level]:
        lo, hi = _p(level, "interval")
        workouts.append({
            "name": f"Yasso 800s x{reps}",
            "category": "yasso",
            "level": level,
            "description": f"Classic marathon predictor. 800m reps with equal rest.",
            "steps": [
                warmup_dist(2),
                step(DURATION_DISTANCE, distance_meters(0.8),
                     TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                     "800m hard"),
                step(DURATION_TIME, time_seconds(3.5),
                     TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                     "Jog recovery (equal time)"),
                repeat_step(1, reps),
                cooldown_dist(2),
            ],
        })
    return workouts


def _pre_race_shakeout(level):
    """Pre-race shakeout runs."""
    configs = {
        "beginner":     3,
        "intermediate": 4,
        "advanced":     5,
    }
    km = configs[level]
    lo, hi = _p(level, "easy")
    lo_s, hi_s = _p(level, "strides")
    return [{
        "name": "Pre-Race Shakeout",
        "category": "shakeout",
        "level": level,
        "description": "Day-before-race loosener. Short and easy with a few openers.",
        "steps": [
            step(DURATION_DISTANCE, distance_meters(km),
                 TARGET_SPEED, 0, lo, hi, INTENSITY_ACTIVE,
                 "Very easy jog"),
            step(DURATION_DISTANCE, distance_meters(0.1),
                 TARGET_SPEED, 0, lo_s, hi_s, INTENSITY_ACTIVE,
                 "Stride opener"),
            step(DURATION_DISTANCE, distance_meters(0.1),
                 TARGET_OPEN, 0, 0, 0, INTENSITY_REST,
                 "Walk"),
            repeat_step(1, 4),
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
    """Build the complete workout library across all levels."""
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

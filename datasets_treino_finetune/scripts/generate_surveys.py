#!/usr/bin/env python3
"""
generate_surveys.py — Phase 1 of the CaForB fine-tuning data pipeline.

Generates 504 structured corporate survey inputs covering every combination of
the three core constraint dimensions (riskAppetite × strategicPriority × regulatoryEnvironment)
while maintaining balanced distributions across sectors, sizes, and competitive pressure levels.

Output: raw_inputs.json (array of survey objects matching frontend AssessmentFormData)
"""

import json
import random
import math
from pathlib import Path
from collections import defaultdict
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_PATH = BASE_DIR / "raw_inputs.json"

SECTORS = [
    "Agriculture, Forestry & Fishing",
    "Mining & Extraction",
    "Manufacturing",
    "Construction",
    "Energy & Utilities",
    "Retail & Wholesale Trade",
    "E-commerce",
    "Transportation & Logistics",
    "Hospitality & Tourism",
    "Information Technology",
    "SaaS / Software",
    "Telecommunications",
    "Fintech",
    "Financial Services",
    "Insurance",
    "Real Estate",
    "Professional & Consulting Services",
    "Legal Services",
    "Education",
    "Healthtech",
    "Healthcare & Medical",
    "Pharmaceuticals & Biotech",
    "Arts, Entertainment & Media",
    "Public Administration",
    "Nonprofit / NGO",
    "Other",
]

SECTOR_TO_FILE = {
    "Agriculture, Forestry & Fishing":          "agriculture_forestry_fishing",
    "Mining & Extraction":                      "mining_extraction",
    "Manufacturing":                            "manufacturing",
    "Construction":                             "construction",
    "Energy & Utilities":                       "energy_utilities",
    "Retail & Wholesale Trade":                 "retail_wholesale_trade",
    "E-commerce":                               "ecommerce",
    "Transportation & Logistics":               "transportation_logistics",
    "Hospitality & Tourism":                    "hospitality_tourism",
    "Information Technology":                   "information_technology",
    "SaaS / Software":                          "saas_software",
    "Telecommunications":                       "telecommunications",
    "Fintech":                                  "fintech",
    "Financial Services":                      "financial_services",
    "Insurance":                               "insurance",
    "Real Estate":                              "real_estate",
    "Professional & Consulting Services":       "professional_consulting",
    "Legal Services":                           "legal_services",
    "Education":                                "education",
    "Healthtech":                               "healthtech",
    "Healthcare & Medical":                     "healthcare_medical",
    "Pharmaceuticals & Biotech":                "pharmaceuticals_biotech",
    "Arts, Entertainment & Media":              "arts_entertainment_media",
    "Public Administration":                    "public_administration",
    "Nonprofit / NGO":                          "nonprofit_ngo",
    "Other":                                    "other",
}

SIZES = ["Micro", "Small", "Medium", "Large"]
RISK_APPETITES = ["conservative", "balanced", "bold"]
STRATEGIC_PRIORITIES = ["growth", "efficiency", "market_defense", "diversification"]
REGULATORY_ENVIRONMENTS = ["low", "medium", "high"]
COMPETITIVE_PRESSURES = ["low", "medium", "high"]
INNOVATION_PROCESSES = ["none", "informal", "partial", "formal"]
CUSTOMER_FEEDBACKS = ["no_formal_process", "informal_conversations", "surveys_nps", "dedicated_research"]
TIME_HORIZONS = ["short", "medium", "long"]
DECISION_MAKINGS = ["owner_alone", "small_leadership_team", "formal_committee", "varies_by_project"]
DIGITAL_MATURITIES = ["1", "2", "3", "4"]
ALL_BARRIERS = ["budget", "talent", "process", "culture", "time", "strategy"]

VARIANTS_PER_COMBO = 14
TOTAL_COMBOS = len(RISK_APPETITES) * len(STRATEGIC_PRIORITIES) * len(REGULATORY_ENVIRONMENTS)

random.seed(42)  # reproducible generation


# ──────────────────────────────────────────────────────────────────────
# Template Loader
# ──────────────────────────────────────────────────────────────────────

class TemplateLoader:
    """Loads all free-text templates from the templates/ directory."""

    def __init__(self, base: Path):
        self._cache: dict[str, list[str]] = {}

    def _load(self, rel_path: str) -> list[str]:
        path = TEMPLATES_DIR / rel_path
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["variants"]

    def sector_desc(self, sector: str) -> str:
        filename = SECTOR_TO_FILE[sector]
        cache_key = f"company_description/by_sector/{filename}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load(f"company_description/by_sector/{filename}.json")
        return random.choice(self._cache[cache_key])

    def size_desc(self, size: str) -> str:
        cache_key = f"company_description/by_size/{size.lower()}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load(f"company_description/by_size/{size.lower()}.json")
        return random.choice(self._cache[cache_key])

    def strategic_goals(self, priority: str) -> str:
        cache_key = f"strategic_goals/{priority}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load(f"strategic_goals/{priority}.json")
        return random.choice(self._cache[cache_key])

    def past_initiatives(self, level: str) -> str:
        cache_key = f"past_initiatives/{level}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load(f"past_initiatives/{level}.json")
        return random.choice(self._cache[cache_key])

    def team_size_desc(self, size: str) -> str:
        cache_key = f"team_size/{size.lower()}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load(f"team_size/{size.lower()}.json")
        return random.choice(self._cache[cache_key])

    def additional_context(self) -> str | None:
        if random.random() > 0.3:
            return None
        category = random.choice(["fundraising", "restructuring", "regulatory_change"])
        cache_key = f"additional_context/{category}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load(f"additional_context/{category}.json")
        return random.choice(self._cache[cache_key])


# ──────────────────────────────────────────────────────────────────────
# Balanced Distribution Tracker
# ──────────────────────────────────────────────────────────────────────

class DistributionTracker:
    """Tracks counts per bucket and picks from the least-represented bucket."""

    def __init__(self):
        self.counts: defaultdict[str, int] = defaultdict(int)

    def pick_balanced(self, pool: list[str]) -> str:
        if not pool:
            raise ValueError("pick_balanced called with empty pool")
        for v in pool:
            self.counts.setdefault(v, 0)
        min_c = min(self.counts[v] for v in pool)
        candidates = [v for v in pool if self.counts[v] == min_c]
        chosen = random.choice(candidates)
        self.counts[chosen] += 1
        return chosen

    def pick_weighted(self, pool: list[str]) -> str:
        chosen = random.choice(pool)
        self.counts[chosen] += 1
        return chosen


# ──────────────────────────────────────────────────────────────────────
# Correlated Field Derivations
# ──────────────────────────────────────────────────────────────────────

def derive_revenue(size: str) -> str:
    mapping = {
        "Micro":  {"under_1m": 0.80, "1m_to_10m": 0.20},
        "Small":  {"under_1m": 0.15, "1m_to_10m": 0.70, "10m_to_50m": 0.15},
        "Medium": {"1m_to_10m": 0.30, "10m_to_50m": 0.60, "over_50m": 0.10},
        "Large":  {"10m_to_50m": 0.30, "over_50m": 0.70},
    }
    options, weights = zip(*mapping[size].items())
    return random.choices(options, weights=weights, k=1)[0]


def derive_budget(risk: str) -> int:
    # triangular distribution via Beta, clamped to 0-30
    params = {
        "conservative": (2, 3, 6),
        "balanced":     (4, 8, 15),
        "bold":         (8, 15, 30),
    }
    lo, mode, hi = params[risk]
    u = random.random()
    if u < (mode - lo) / (hi - lo):
        val = lo + math.sqrt(u * (hi - lo) * (mode - lo))
    else:
        val = hi - math.sqrt((1 - u) * (hi - lo) * (hi - mode))
    return max(0, min(30, round(val)))


def derive_innovation_process() -> str:
    return random.choices(
        INNOVATION_PROCESSES, weights=[0.10, 0.25, 0.40, 0.25], k=1
    )[0]


def derive_feedback(process: str) -> str:
    mapping = {
        "none":     {"no_formal_process": 0.80, "informal_conversations": 0.20},
        "informal": {"no_formal_process": 0.15, "informal_conversations": 0.60, "surveys_nps": 0.25},
        "partial":  {"informal_conversations": 0.30, "surveys_nps": 0.50, "dedicated_research": 0.20},
        "formal":   {"informal_conversations": 0.10, "surveys_nps": 0.40, "dedicated_research": 0.50},
    }
    options, weights = zip(*mapping[process].items())
    return random.choices(options, weights=weights, k=1)[0]


def derive_digital(process: str, size: str) -> str:
    base = {"none": 1, "informal": 1.5, "partial": 2.5, "formal": 3.5}[process]
    size_modifier = {"Micro": -0.5, "Small": 0, "Medium": 0.5, "Large": 1.0}[size]
    val = base + size_modifier + random.uniform(-0.4, 0.4)
    clamped = max(1, min(4, round(val)))
    return str(clamped)


def derive_decision(size: str) -> str:
    mapping = {
        "Micro":  {"owner_alone": 0.75, "small_leadership_team": 0.25},
        "Small":  {"owner_alone": 0.30, "small_leadership_team": 0.60, "formal_committee": 0.10},
        "Medium": {"small_leadership_team": 0.50, "formal_committee": 0.35, "varies_by_project": 0.15},
        "Large":  {"small_leadership_team": 0.10, "formal_committee": 0.50, "varies_by_project": 0.40},
    }
    options, weights = zip(*mapping[size].items())
    return random.choices(options, weights=weights, k=1)[0]


def derive_time_horizon() -> str:
    return random.choices(TIME_HORIZONS, weights=[0.30, 0.45, 0.25], k=1)[0]


def derive_barriers(process: str, regulatory: str, comp_press: str) -> list[str]:
    weights = {b: 0.15 for b in ALL_BARRIERS}

    if regulatory == "high":
        weights["process"] += 0.30
        weights["strategy"] += 0.15
    if comp_press == "high":
        weights["time"] += 0.25
    if comp_press == "low":
        weights["time"] -= 0.10
    if process == "none":
        weights["culture"] += 0.30
        weights["strategy"] += 0.20
    if process == "formal":
        weights["process"] -= 0.10
        weights["talent"] += 0.15

    clamped = {k: max(0.0, min(1.0, v)) for k, v in weights.items()}

    n_barriers = random.choices([1, 2, 3, 4], weights=[0.10, 0.30, 0.40, 0.20], k=1)[0]
    selected = set()
    pool = list(ALL_BARRIERS)
    while len(selected) < n_barriers:
        probs = [clamped[b] for b in pool]
        total = sum(probs)
        if total == 0:
            probs = [1.0 / len(pool)] * len(pool)
        else:
            probs = [p / total for p in probs]
        chosen = random.choices(pool, weights=probs, k=1)[0]
        selected.add(chosen)
        pool.remove(chosen)

    return sorted(selected)


# ──────────────────────────────────────────────────────────────────────
# Company Name Generator
# ──────────────────────────────────────────────────────────────────────

NAME_PREFIXES = [
    "Nova", "Atlas", "Vertex", "Core", "Prime", "Apex", "Fusion", "Orbit",
    "Strato", "Lumina", "Quantum", "Nexus", "Titan", "Vanguard", "Pioneer",
    "Catalyst", "Forge", "Ember", "Aether", "Helix", "Crest", "Pulse",
    "Meridian", "Synapse", "Vault", "Element", "Beacon", "Cipher", "Grid", "Anchor",
]

NAME_SUFFIXES = [
    "Technologies", "Solutions", "Group", "Systems", "Innovations",
    "Industries", "Labs", "Dynamics", "Partners", "Holdings",
    "Ventures", "Corporation", "Services", "Enterprises", "Analytics",
    "Consulting", "Networks", "Digital", "Capital", "",
]

NAME_TLDS = [".com", ".io", ".ai", ".co", ".tech", ""]


def generate_company_name(sector: str) -> str:
    prefix = random.choice(NAME_PREFIXES)
    suffix = random.choice(NAME_SUFFIXES)
    suffix = suffix if random.random() < 0.7 else ""
    base = f"{prefix} {suffix}".strip()
    tld = random.choice(NAME_TLDS) if random.random() < 0.3 else ""
    return f"{base}{tld}"


# ──────────────────────────────────────────────────────────────────────
# Main Generator
# ──────────────────────────────────────────────────────────────────────

def generate_all() -> list[dict[str, Any]]:
    loader = TemplateLoader(TEMPLATES_DIR)
    sector_tracker = DistributionTracker()
    size_tracker = DistributionTracker()
    comp_tracker = DistributionTracker()

    all_examples: list[dict[str, Any]] = []

    combo_pool: list[tuple[str, str, str]] = []
    for risk in RISK_APPETITES:
        for prio in STRATEGIC_PRIORITIES:
            for reg in REGULATORY_ENVIRONMENTS:
                combo_pool.append((risk, prio, reg))

    for combo_idx, (risk, prio, reg) in enumerate(combo_pool):
        combo_id = f"{risk}|{prio}|{reg}"
        for variant_i in range(VARIANTS_PER_COMBO):
            sector = sector_tracker.pick_balanced(SECTORS)
            size = size_tracker.pick_balanced(SIZES)
            comp_press = comp_tracker.pick_balanced(COMPETITIVE_PRESSURES)

            process = derive_innovation_process()
            process_level = {"none": "none", "informal": "low", "partial": "medium", "formal": "high"}[process]

            revenue = derive_revenue(size)
            budget = derive_budget(risk)
            decision = derive_decision(size)
            feedback = derive_feedback(process)
            digital = derive_digital(process, size)
            time_h = derive_time_horizon()
            barriers = derive_barriers(process, reg, comp_press)

            description = f"{loader.sector_desc(sector)} {loader.size_desc(size)}".strip()
            goals = loader.strategic_goals(prio)
            past = loader.past_initiatives(process_level)
            team = loader.team_size_desc(size)
            extra = loader.additional_context()

            example = {
                "combo_id": combo_id,
                "variant_index": variant_i,
                "fields": {
                    "companyName": generate_company_name(sector),
                    "sector": sector,
                    "size": size,
                    "regulatoryEnvironment": reg,
                    "companyDescription": description,
                    "innovationProcess": process,
                    "pastInitiatives": past,
                    "customerFeedback": feedback,
                    "strategicGoals": goals,
                    "strategicPriority": prio,
                    "timeHorizon": time_h,
                    "riskAppetite": risk,
                    "teamSize": team,
                    "digitalMaturity": digital,
                    "revenueRange": revenue,
                    "budgetPercentage": budget,
                    "decisionMaking": decision,
                    "mainBarrier": barriers,
                    "competitivePressure": comp_press,
                    "additionalContext": extra or "",
                },
            }
            all_examples.append(example)

    random.shuffle(all_examples)

    for i, ex in enumerate(all_examples):
        ex["id"] = f"{i + 1:04d}"

    return all_examples


# ──────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────────────────────────────

def print_distribution(examples: list[dict]) -> None:
    fields_to_report = [
        ("sector", SECTORS),
        ("size", SIZES),
        ("riskAppetite", RISK_APPETITES),
        ("strategicPriority", STRATEGIC_PRIORITIES),
        ("regulatoryEnvironment", REGULATORY_ENVIRONMENTS),
        ("competitivePressure", COMPETITIVE_PRESSURES),
    ]
    for field_name, pool in fields_to_report:
        counts = defaultdict(int)
        for ex in examples:
            counts[ex["fields"][field_name]] += 1
        print(f"\n  {field_name}:")
        for val in pool:
            bar = "#" * counts[val]
            print(f"    {val:<22} {counts[val]:>3}  {bar}")

    combos = defaultdict(int)
    for ex in examples:
        combos[ex["combo_id"]] += 1
    print(f"\n  Constraint combos ({TOTAL_COMBOS}):")
    min_c, max_c = min(combos.values()), max(combos.values())
    print(f"    Min: {min_c}  Max: {max_c}  Expected: {VARIANTS_PER_COMBO}")


def main():
    print(f"Generating {TOTAL_COMBOS} combos × {VARIANTS_PER_COMBO} variants = "
          f"{TOTAL_COMBOS * VARIANTS_PER_COMBO} survey inputs…")
    examples = generate_all()
    print(f"Generated {len(examples)} examples.")
    print_distribution(examples)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

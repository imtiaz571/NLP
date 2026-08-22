"""
NPC Talk — Data Audit & Validation Tool
Validates personas, training datasets, memory stores, and character assets
against the canonical 6-character roster (ash, finn, eva, sam, tabitha, pip).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

CANONICAL_NPCS = ["ash", "finn", "eva", "sam", "tabitha", "pip"]
FORBIDDEN_NAMES = ["henry", "max", "brynn", "mirael", "shadow_vex", "mara_cole", "ruth"]

REQUIRED_PERSONA_KEYS = [
    "id", "name", "title", "backstory", "personality_traits",
    "speech_style", "goals", "relationships", "example_lines"
]

def main():
    critical_issues = []
    warnings = []

    print("=" * 60)
    print("  NPC TALK — DATA & PERSONA INTEGRITY AUDIT")
    print("=" * 60)

    # 1. Validate Persona JSON files
    persona_dir = ROOT / "src" / "npc_talk" / "personas"
    if not persona_dir.exists():
        critical_issues.append("Missing 'personas/' directory.")
    else:
        persona_files = list(persona_dir.glob("*.json"))
        persona_ids = [f.stem for f in persona_files]

        # Check for missing canonical personas
        for c_id in CANONICAL_NPCS:
            if c_id not in persona_ids:
                critical_issues.append(f"Missing canonical persona file: personas/{c_id}.json")

        # Check for extra/orphaned personas
        for p_file in persona_files:
            p_id = p_file.stem
            if p_id not in CANONICAL_NPCS:
                critical_issues.append(f"Orphaned/non-canonical persona found: {p_file.name}")
            else:
                try:
                    data = json.loads(p_file.read_text(encoding="utf-8"))
                    for req_k in REQUIRED_PERSONA_KEYS:
                        if req_k not in data:
                            critical_issues.append(f"Persona '{p_id}' missing required key: '{req_k}'")
                    
                    # Validate relationships only point to valid NPCs
                    rel = data.get("relationships", {})
                    for target_npc in rel.keys():
                        if target_npc not in CANONICAL_NPCS or target_npc == p_id:
                            warnings.append(f"Persona '{p_id}' has invalid relationship target: '{target_npc}'")
                    
                    # Check for forbidden names in prose
                    text_str = json.dumps(data).lower()
                    for term in FORBIDDEN_NAMES:
                        if re.search(r"\b" + re.escape(term) + r"\b", text_str):
                            critical_issues.append(f"Persona '{p_id}' contains forbidden character reference: '{term}'")

                except Exception as exc:
                    critical_issues.append(f"Error parsing personas/{p_file.name}: {exc}")

    # 2. Validate Training Dataset (data/npc_dialogue_training.json)
    train_file = ROOT / "data" / "npc_dialogue_training.json"
    if not train_file.exists():
        warnings.append("data/npc_dialogue_training.json not found")
    else:
        try:
            train_data = json.loads(train_file.read_text(encoding="utf-8"))
            dataset_npcs = list(train_data.get("npcs", {}).keys())
            for c_id in CANONICAL_NPCS:
                if c_id not in dataset_npcs:
                    warnings.append(f"Canonical NPC '{c_id}' missing in training dataset")
            for d_id in dataset_npcs:
                if d_id not in CANONICAL_NPCS:
                    critical_issues.append(f"Non-canonical NPC '{d_id}' found in training dataset 'npcs' dict")
        except Exception as exc:
            critical_issues.append(f"Error parsing npc_dialogue_training.json: {exc}")

    # 3. Validate Memory Metadata (src/npc_talk/memory/store/metadata.json)
    meta_file = ROOT / "src" / "npc_talk" / "memory" / "store" / "metadata.json"
    if meta_file.exists():
        try:
            meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
            for idx, entry in enumerate(meta_data):
                nid = entry.get("npc_id")
                if nid not in CANONICAL_NPCS:
                    critical_issues.append(f"metadata.json entry #{idx} has invalid npc_id: '{nid}'")
        except Exception as exc:
            critical_issues.append(f"Error reading memory/store/metadata.json: {exc}")

    # 4. Validate Character Asset Directories (frontend/assets/characters/)
    char_asset_dir = ROOT / "frontend" / "assets" / "characters"
    if char_asset_dir.exists():
        asset_folders = [d.name for d in char_asset_dir.iterdir() if d.is_dir()]
        for f_name in asset_folders:
            if f_name not in CANONICAL_NPCS:
                critical_issues.append(f"Orphaned character asset folder found: frontend/assets/characters/{f_name}/")

    # 5. Summary Report
    print(f"\nAudit completed across personas, dataset, memory, and assets.")
    print(f"Canonical NPC Roster: {', '.join(CANONICAL_NPCS)}")
    print("-" * 60)
    print(f"Critical Issues: {len(critical_issues)}")
    print(f"Warnings:        {len(warnings)}")
    print("-" * 60)

    if critical_issues:
        print("\n[CRITICAL ISSUES]")
        for issue in critical_issues:
            print(f"  [X] {issue}")

    if warnings:
        print("\n[WARNINGS]")
        for warn in warnings:
            print(f"  [!] {warn}")

    if not critical_issues and not warnings:
        print("\n[PASS] All data checks passed with 0 critical issues and 0 warnings!")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())

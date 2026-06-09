import csv
import json
from collections import Counter

INPUT_FILE = "data/interactions_final_unique_users.csv"
OUTPUT_FILE = "results_final/results.json"

counts = Counter()

total_rows = 0


with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        total_rows += 1

        interaction = (row.get("user_interaction_side") or "").strip()
        if interaction:
            counts[interaction] += 1


left_left = counts["left->left"]
right_right = counts["right->right"]
left_right = counts["left->right"]
right_left = counts["right->left"]

total = left_left + right_right + left_right + right_left

within = left_left + right_right
cross = left_right + right_left

def safe_pct(x):
    return round((x / total) * 100, 2) if total else 0

results = {
    "total_rows": total_rows,
    "total_interactions": total,

    "interaction_counts": {
        "left_left": left_left,
        "right_right": right_right,
        "left_right": left_right,
        "right_left": right_left
    },

    "interaction_percentages": {
        "left_left_pct": safe_pct(left_left),
        "right_right_pct": safe_pct(right_right),
        "left_right_pct": safe_pct(left_right),
        "right_left_pct": safe_pct(right_left)
    },

    "group_summary": {
        "within_count": within,
        "cross_count": cross,
        "within_pct": safe_pct(within),
        "cross_pct": safe_pct(cross)
    }
}

# =========================
# שמירה
# =========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print("Done")
print(f"Created: {OUTPUT_FILE}")
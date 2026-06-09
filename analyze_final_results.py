import csv
import json
import os
import random
import statistics
from collections import Counter, defaultdict

INPUT_FILE = "data/interactions_final_unique_users.csv"
OUTPUT_DIR = "results_balanced_average"

RUNS = 10
SAMPLE_SIZE = 3000
RANDOM_SEED = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)
random.seed(RANDOM_SEED)


def clean_fieldnames(reader):
    reader.fieldnames = [name.strip() for name in reader.fieldnames]
    return reader


def get_col(row, *names):
    for name in names:
        if name in row:
            return (row.get(name) or "").strip()
    return ""


def safe_pct(value, total):
    return round((value / total) * 100, 2) if total else 0


rows = []

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    reader = clean_fieldnames(reader)

    print("Columns:")
    print(reader.fieldnames)

    for row in reader:
        source_user = get_col(row, "source_user", "comment_author")
        target_user = get_col(row, "target_user", "parent_author")

        source_side = get_col(row, "source_user_side", "comment_user_final_side", "comment_text_side")
        target_side = get_col(row, "target_user_side", "parent_user_final_side", "parent_text_side")

        interaction = get_col(row, "user_interaction_side", "interaction_side_text", "interaction_side")

        if not interaction and source_side in ["left", "right"] and target_side in ["left", "right"]:
            interaction = f"{source_side}->{target_side}"

        if source_user and target_user and interaction in {
            "left->left",
            "right->right",
            "left->right",
            "right->left"
        }:
            rows.append({
                "source_user": source_user,
                "target_user": target_user,
                "source_side": source_side,
                "target_side": target_side,
                "interaction": interaction
            })

print(f"\nLoaded valid rows: {len(rows):,}")

left_users = sorted({r["source_user"] for r in rows if r["source_side"] == "left"})
right_users = sorted({r["source_user"] for r in rows if r["source_side"] == "right"})

print(f"Left users: {len(left_users):,}")
print(f"Right users: {len(right_users):,}")

actual_sample_size = min(SAMPLE_SIZE, len(left_users), len(right_users))

if actual_sample_size == 0:
    raise ValueError("No users found for sampling. Check column names and side values.")

print(f"\nUsing sample size: {actual_sample_size:,} left vs {actual_sample_size:,} right")
print(f"Runs: {RUNS}")

run_results = []

for run in range(1, RUNS + 1):
    sampled_left = set(random.sample(left_users, actual_sample_size))
    sampled_right = set(random.sample(right_users, actual_sample_size))
    sampled_users = sampled_left | sampled_right

    counts = Counter()

    for r in rows:
        if r["source_user"] not in sampled_users:
            continue

        counts[r["interaction"]] += 1

    left_left = counts["left->left"]
    right_right = counts["right->right"]
    left_right = counts["left->right"]
    right_left = counts["right->left"]

    total = left_left + right_right + left_right + right_left
    within = left_left + right_right
    cross = left_right + right_left

    result = {
        "run": run,
        "total_interactions": total,
        "interaction_counts": {
            "left_left": left_left,
            "right_right": right_right,
            "left_right": left_right,
            "right_left": right_left
        },
        "interaction_percentages": {
            "left_left_pct": safe_pct(left_left, total),
            "right_right_pct": safe_pct(right_right, total),
            "left_right_pct": safe_pct(left_right, total),
            "right_left_pct": safe_pct(right_left, total)
        },
        "group_summary": {
            "within_count": within,
            "cross_count": cross,
            "within_pct": safe_pct(within, total),
            "cross_pct": safe_pct(cross, total)
        }
    }

    run_results.append(result)

    print(f"\nRun {run}:")
    print(f"Total: {total:,}")
    print(f"Left->Left: {left_left:,} ({safe_pct(left_left, total)}%)")
    print(f"Right->Right: {right_right:,} ({safe_pct(right_right, total)}%)")
    print(f"Left->Right: {left_right:,} ({safe_pct(left_right, total)}%)")
    print(f"Right->Left: {right_left:,} ({safe_pct(right_left, total)}%)")
    print(f"Within: {within:,} ({safe_pct(within, total)}%)")
    print(f"Cross: {cross:,} ({safe_pct(cross, total)}%)")


def avg(path):
    return round(statistics.mean(path), 2) if path else 0


def avg_int(path):
    return round(statistics.mean(path)) if path else 0


average_summary = {
    "sample_settings": {
        "runs": RUNS,
        "requested_sample_size": SAMPLE_SIZE,
        "actual_sample_size_each_side": actual_sample_size,
        "left_users_available": len(left_users),
        "right_users_available": len(right_users)
    },
    "total_rows": avg_int([r["total_interactions"] for r in run_results]),
    "total_interactions": avg_int([r["total_interactions"] for r in run_results]),
    "interaction_counts": {
        "left_left": avg_int([r["interaction_counts"]["left_left"] for r in run_results]),
        "right_right": avg_int([r["interaction_counts"]["right_right"] for r in run_results]),
        "left_right": avg_int([r["interaction_counts"]["left_right"] for r in run_results]),
        "right_left": avg_int([r["interaction_counts"]["right_left"] for r in run_results])
    },
    "interaction_percentages": {
        "left_left_pct": avg([r["interaction_percentages"]["left_left_pct"] for r in run_results]),
        "right_right_pct": avg([r["interaction_percentages"]["right_right_pct"] for r in run_results]),
        "left_right_pct": avg([r["interaction_percentages"]["left_right_pct"] for r in run_results]),
        "right_left_pct": avg([r["interaction_percentages"]["right_left_pct"] for r in run_results])
    },
    "group_summary": {
        "within_count": avg_int([r["group_summary"]["within_count"] for r in run_results]),
        "cross_count": avg_int([r["group_summary"]["cross_count"] for r in run_results]),
        "within_pct": avg([r["group_summary"]["within_pct"] for r in run_results]),
        "cross_pct": avg([r["group_summary"]["cross_pct"] for r in run_results])
    }
}

output = {
    "average_results": average_summary,
    "all_runs": run_results
}

with open(os.path.join(OUTPUT_DIR, "balanced_average_results.json"), "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

with open(os.path.join(OUTPUT_DIR, "balanced_average_readable.txt"), "w", encoding="utf-8") as f:
    f.write("===== BALANCED SAMPLING AVERAGE RESULTS =====\n\n")
    f.write(f"Runs: {RUNS}\n")
    f.write(f"Sample size each side: {actual_sample_size:,}\n\n")

    f.write(json.dumps(average_summary, indent=4, ensure_ascii=False))

print("\n==============================")
print("FINAL AVERAGE RESULTS")
print("==============================")
print(json.dumps(average_summary, indent=4, ensure_ascii=False))

print("\nDone.")
print(f"Created: {OUTPUT_DIR}/balanced_average_results.json")
print(f"Created: {OUTPUT_DIR}/balanced_average_readable.txt")
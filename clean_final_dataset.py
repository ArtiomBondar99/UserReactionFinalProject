import csv

INPUT_FILE = "data/interactions_known_users_only.csv"
OUTPUT_FILE = "data/interactions_final_minimal.csv"

KEEP_COLUMNS = [
    "comment_author",
    "parent_author",
    "source_user_side",
    "target_user_side",
    "user_interaction_side",
    "comment_body",
    "parent_text",
    "parent_type"
]

total = 0
written = 0

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as outfile:

    reader = csv.DictReader(infile)

    fieldnames = KEEP_COLUMNS + ["interaction_level"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        total += 1

        new_row = {col: row.get(col, "") for col in KEEP_COLUMNS}

        parent_type = (row.get("parent_type") or "").strip().lower()

        if parent_type == "post":
            level = "reply_to_post"
        elif parent_type == "comment":
            level = "reply_to_comment"
        else:
            level = "unknown"

        new_row["interaction_level"] = level

        writer.writerow(new_row)
        written += 1


print("Done")
print(f"Original rows: {total}")
print(f"Clean rows: {written}")
print(f"Created: {OUTPUT_FILE}")
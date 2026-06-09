import csv

INTERACTIONS_FILE = "data/interactions_clean_text_checked.csv"
USERS_FILE = "data/users_final_side.csv"
OUTPUT_FILE = "data/interactions_known_users_only.csv"

user_side = {}

with open(USERS_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        user = (row.get("user") or "").strip()
        side = (row.get("final_side") or "").strip()

        if side in {"left", "right"}:
            user_side[user] = side


total = 0
written = 0

with open(INTERACTIONS_FILE, "r", encoding="utf-8-sig", newline="") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as outfile:

    reader = csv.DictReader(infile)

    fieldnames = reader.fieldnames + [
        "source_user_side",
        "target_user_side",
        "user_interaction_side"
    ]

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        total += 1

        source_user = (row.get("comment_author") or "").strip()
        target_user = (row.get("parent_author") or "").strip()

        if source_user not in user_side:
            continue

        if target_user not in user_side:
            continue

        source_side = user_side[source_user]
        target_side = user_side[target_user]

        row["source_user_side"] = source_side
        row["target_user_side"] = target_side
        row["user_interaction_side"] = f"{source_side}->{target_side}"

        writer.writerow(row)
        written += 1


print("Done")
print(f"Total rows: {total}")
print(f"Filtered (known users only): {written}")
print(f"Created: {OUTPUT_FILE}")
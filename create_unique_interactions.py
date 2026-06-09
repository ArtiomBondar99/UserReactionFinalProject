import csv

INPUT_FILE = "data/interactions_final_minimal.csv"
OUTPUT_FILE = "data/interactions_final_unique_users.csv"

seen_pairs = set()

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    total = 0
    written = 0

    for row in reader:
        total += 1

        source = (row.get("comment_author") or "").strip()
        target = (row.get("parent_author") or "").strip()

        if not source or not target:
            continue

        pair = (source, target)

        if pair in seen_pairs:
            continue

        seen_pairs.add(pair)

        writer.writerow(row)
        written += 1

print("Done")
print(f"Original rows: {total}")
print(f"Unique interactions: {written}")
print(f"Created: {OUTPUT_FILE}")
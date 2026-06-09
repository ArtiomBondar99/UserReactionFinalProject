import csv
from collections import defaultdict

INPUT_FILE = "data/interactions_clean.csv"
OUTPUT_FILE = "data/interactions_clean_text_checked.csv"
USERS_FILE = "data/users_final_side.csv"

MIN_POLITICAL_COMMENTS = 3
MAJORITY_THRESHOLD = 0.6

LEFT_KEYWORDS = [
    "biden", "harris", "democrat", "democrats", "liberal",
    "progressive", "left", "abortion rights", "climate change",
    "gun control", "lgbtq", "healthcare"
]

RIGHT_KEYWORDS = [
    "trump", "maga", "republican", "republicans", "conservative",
    "right", "border", "illegal immigration", "second amendment",
    "pro life", "tax cuts"
]

NEGATIVE_WORDS = [
    "bad", "hate", "wrong", "corrupt", "liar", "stupid",
    "terrible", "worst", "criminal", "fake", "against"
]

POSITIVE_WORDS = [
    "good", "great", "support", "agree", "true",
    "best", "strong", "smart"
]


def classify_text(text):
    text = (text or "").lower()

    left_score = sum(1 for w in LEFT_KEYWORDS if w in text)
    right_score = sum(1 for w in RIGHT_KEYWORDS if w in text)

    positive_score = sum(1 for w in POSITIVE_WORDS if w in text)
    negative_score = sum(1 for w in NEGATIVE_WORDS if w in text)

    if left_score > right_score and positive_score >= negative_score:
        return "left"

    if left_score > right_score and negative_score > positive_score:
        return "right"

    if right_score > left_score and positive_score >= negative_score:
        return "right"

    if right_score > left_score and negative_score > positive_score:
        return "left"

    return "unknown"


user_counts = defaultdict(lambda: {
    "left": 0,
    "right": 0,
    "unknown": 0
})

rows = []

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as infile:
    reader = csv.DictReader(infile)

    new_columns = [
        "comment_text_side",
        "parent_text_side",
        "post_text_side",
        "interaction_side_text"
    ]

    fieldnames = reader.fieldnames + new_columns

    total = 0

    for row in reader:
        total += 1

        comment_author = (row.get("comment_author") or "").strip()

        comment_side = classify_text(row.get("comment_body", ""))
        parent_side = classify_text(row.get("parent_text", ""))
        post_side = classify_text(row.get("post_text", ""))

        interaction_side_text = ""
        if comment_side != "unknown" and parent_side != "unknown":
            interaction_side_text = f"{comment_side}->{parent_side}"

        row["comment_text_side"] = comment_side
        row["parent_text_side"] = parent_side
        row["post_text_side"] = post_side
        row["interaction_side_text"] = interaction_side_text

        rows.append(row)

        if comment_author and comment_author != "[deleted]":
            if comment_side == "left":
                user_counts[comment_author]["left"] += 1
            elif comment_side == "right":
                user_counts[comment_author]["right"] += 1
            else:
                user_counts[comment_author]["unknown"] += 1

        if total % 100000 == 0:
            print(f"Checked: {total:,}")


with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


with open(USERS_FILE, "w", encoding="utf-8-sig", newline="") as outfile:
    fieldnames_users = [
        "user",
        "left_count",
        "right_count",
        "unknown_count",
        "total_political",
        "left_percent",
        "right_percent",
        "final_side"
    ]

    writer = csv.DictWriter(outfile, fieldnames=fieldnames_users)
    writer.writeheader()

    for user, counts in user_counts.items():
        left_count = counts["left"]
        right_count = counts["right"]
        unknown_count = counts["unknown"]

        total_political = left_count + right_count

        if total_political < MIN_POLITICAL_COMMENTS:
            final_side = "unknown"
            left_percent = 0
            right_percent = 0
        else:
            left_percent = round(left_count / total_political, 3)
            right_percent = round(right_count / total_political, 3)

            if left_percent >= MAJORITY_THRESHOLD:
                final_side = "left"
            elif right_percent >= MAJORITY_THRESHOLD:
                final_side = "right"
            else:
                final_side = "mixed"

        writer.writerow({
            "user": user,
            "left_count": left_count,
            "right_count": right_count,
            "unknown_count": unknown_count,
            "total_political": total_political,
            "left_percent": left_percent,
            "right_percent": right_percent,
            "final_side": final_side
        })


print("Done.")
print(f"Created: {OUTPUT_FILE}")
print(f"Created: {USERS_FILE}")
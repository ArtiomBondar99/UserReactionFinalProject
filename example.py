import csv
import json
import os
import re
from collections import defaultdict

INPUT_FILE = "data/interactions_final_unique_users.csv"

OUTPUT_DIR = "results_final"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "candidate_stance_clear_examples.csv")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "candidate_stance_clear_examples.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

TOP_N_PER_TYPE = 10

VALID_INTERACTIONS = {
    "pro_trump->pro_trump",
    "pro_kamala->pro_kamala",
    "pro_trump->pro_kamala",
    "pro_kamala->pro_trump"
}


PRO_TRUMP_PHRASES = [
    "vote trump",
    "voting trump",
    "support trump",
    "trump 2024",
    "trump was right",
    "trump is right",
    "trump did a good job",
    "trump will win",
    "trump is better",
    "trump is strong",
    "maga",
    "make america great again",
    "secure the border",
    "border security",
    "illegal immigration",
    "tax cuts",
    "america first"
]

ANTI_TRUMP_PHRASES = [
    "trump is dangerous",
    "trump is a threat",
    "trump lost",
    "trump lied",
    "trump lies",
    "trump is corrupt",
    "trump is unfit",
    "trump is a criminal",
    "anti trump",
    "never trump",
    "against trump",
    "maga cult",
    "trump supporters are",
    "project 2025"
]

PRO_KAMALA_PHRASES = [
    "vote kamala",
    "voting kamala",
    "support kamala",
    "kamala 2024",
    "vote harris",
    "voting harris",
    "support harris",
    "harris 2024",
    "kamala is better",
    "harris is better",
    "kamala will win",
    "harris will win",
    "vote blue",
    "blue downballot",
    "democrats are better",
    "biden harris",
    "pro union",
    "pro labor",
    "women's rights",
    "abortion rights",
    "lgbtq rights",
    "climate change"
]

ANTI_KAMALA_PHRASES = [
    "kamala is bad",
    "kamala is weak",
    "kamala lied",
    "kamala lies",
    "kamala is corrupt",
    "kamala is unfit",
    "kamala is incompetent",
    "harris is bad",
    "harris is weak",
    "harris lied",
    "harris lies",
    "biden is corrupt",
    "biden is weak",
    "democrats are corrupt",
    "democrats lied",
    "democrats lie",
    "liberals are",
    "democrat hoax",
    "open border"
]

CONFLICT_WORDS = [
    "wrong",
    "false",
    "lie",
    "lies",
    "lied",
    "bullshit",
    "nonsense",
    "disagree",
    "not true",
    "you are wrong",
    "fake",
    "corrupt",
    "criminal",
    "dangerous",
    "unfit",
    "incompetent",
    "threat"
]


def clean_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def word_count(text):
    return len(text.split())


def contains_phrase(text, phrases):
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in phrases)


def count_phrases(text, phrases):
    text_lower = text.lower()
    return sum(1 for phrase in phrases if phrase in text_lower)


def short_text(text, max_words=45):
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def stance_scores(text):
    """
    מחזיר ציון תמיכה בטראמפ וציון תמיכה בקמלה.
    תמיכה בטראמפ יכולה להיות:
    1. טקסט בעד Trump
    2. טקסט נגד Kamala/Harris/Biden/Democrats

    תמיכה בקמלה יכולה להיות:
    1. טקסט בעד Kamala/Harris/Biden/Democrats
    2. טקסט נגד Trump/MAGA/Republicans
    """

    pro_trump_score = 0
    pro_kamala_score = 0

    pro_trump_score += count_phrases(text, PRO_TRUMP_PHRASES) * 5
    pro_trump_score += count_phrases(text, ANTI_KAMALA_PHRASES) * 5

    pro_kamala_score += count_phrases(text, PRO_KAMALA_PHRASES) * 5
    pro_kamala_score += count_phrases(text, ANTI_TRUMP_PHRASES) * 5

    return pro_trump_score, pro_kamala_score


def classify_candidate_stance(text):
    pro_trump_score, pro_kamala_score = stance_scores(text)

    if pro_trump_score >= 5 and pro_trump_score > pro_kamala_score:
        return "pro_trump", pro_trump_score, pro_kamala_score

    if pro_kamala_score >= 5 and pro_kamala_score > pro_trump_score:
        return "pro_kamala", pro_trump_score, pro_kamala_score

    return "unknown", pro_trump_score, pro_kamala_score


def has_candidate_conflict(comment_text, parent_text):
    """
    בודק האם יש ויכוח ברור בין הצדדים.
    """
    combined = (comment_text + " " + parent_text).lower()

    has_trump = "trump" in combined or "maga" in combined
    has_kamala = "kamala" in combined or "harris" in combined or "biden" in combined
    has_conflict = contains_phrase(combined, CONFLICT_WORDS)

    return has_trump and has_kamala and has_conflict


def get_col(row, *names):
    for name in names:
        value = row.get(name)
        if value is not None:
            return clean_text(value)
    return ""


examples_by_type = defaultdict(list)

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        source_user = get_col(row, "comment_author", "source_user")
        target_user = get_col(row, "parent_author", "target_user")

        if not source_user or not target_user:
            continue

        if source_user.lower() in ["[deleted]", "automoderator"]:
            continue

        if target_user.lower() in ["[deleted]", "automoderator"]:
            continue

        comment_text = get_col(row, "comment_body", "comment_text")
        parent_text = get_col(row, "parent_text", "parent_body", "submission_title")

        if not comment_text or not parent_text:
            continue

        if comment_text.lower() in ["[deleted]", "[removed]"]:
            continue

        if parent_text.lower() in ["[deleted]", "[removed]"]:
            continue

        # קצר וברור לטבלה
        if word_count(comment_text) < 8 or word_count(parent_text) < 8:
            continue

        if word_count(comment_text) > 100 or word_count(parent_text) > 130:
            continue

        comment_stance, comment_trump_score, comment_kamala_score = classify_candidate_stance(comment_text)
        parent_stance, parent_trump_score, parent_kamala_score = classify_candidate_stance(parent_text)

        if comment_stance == "unknown" or parent_stance == "unknown":
            continue

        candidate_interaction = f"{comment_stance}->{parent_stance}"

        if candidate_interaction not in VALID_INTERACTIONS:
            continue

        same_side = candidate_interaction in [
            "pro_trump->pro_trump",
            "pro_kamala->pro_kamala"
        ]

        cross_side = candidate_interaction in [
            "pro_trump->pro_kamala",
            "pro_kamala->pro_trump"
        ]

        score = 0

        # חוזק עמדה בטקסט התגובה
        score += max(comment_trump_score, comment_kamala_score)

        # חוזק עמדה בטקסט שאליו הגיבו
        score += max(parent_trump_score, parent_kamala_score)

        # עדיפות לטקסט קצר וברור
        if 12 <= word_count(comment_text) <= 60:
            score += 10

        if 12 <= word_count(parent_text) <= 80:
            score += 10

        # באותו צד — נעדיף טקסט שנראה כמו תמיכה או הסכמה
        if same_side:
            if contains_phrase(comment_text, ["agree", "true", "yes", "exactly", "support", "right"]):
                score += 15

        # בין הצדדים — נעדיף ריב ברור
        if cross_side:
            if has_candidate_conflict(comment_text, parent_text):
                score += 25
            else:
                score -= 20

        if score <= 0:
            continue

        example = {
            "candidate_interaction": candidate_interaction,

            "source_user_report": "User A",
            "target_user_report": "User B",

            # לא לשים בספר, רק לבדיקה שלך
            "source_user_original": source_user,
            "target_user_original": target_user,

            "score": score,

            "comment_stance": comment_stance,
            "parent_stance": parent_stance,

            "comment_pro_trump_score": comment_trump_score,
            "comment_pro_kamala_score": comment_kamala_score,
            "parent_pro_trump_score": parent_trump_score,
            "parent_pro_kamala_score": parent_kamala_score,

            "has_candidate_conflict": has_candidate_conflict(comment_text, parent_text),

            "comment_text_short": short_text(comment_text, 45),
            "parent_text_short": short_text(parent_text, 45),

            "comment_text_full": comment_text,
            "parent_text_full": parent_text
        }

        examples_by_type[candidate_interaction].append(example)


final_examples = {}

for interaction_type in [
    "pro_trump->pro_trump",
    "pro_kamala->pro_kamala",
    "pro_trump->pro_kamala",
    "pro_kamala->pro_trump"
]:
    final_examples[interaction_type] = sorted(
        examples_by_type[interaction_type],
        key=lambda x: x["score"],
        reverse=True
    )[:TOP_N_PER_TYPE]


with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(final_examples, f, indent=4, ensure_ascii=False)


fieldnames = [
    "candidate_interaction",
    "source_user_report",
    "target_user_report",
    "source_user_original",
    "target_user_original",
    "score",
    "comment_stance",
    "parent_stance",
    "comment_pro_trump_score",
    "comment_pro_kamala_score",
    "parent_pro_trump_score",
    "parent_pro_kamala_score",
    "has_candidate_conflict",
    "comment_text_short",
    "parent_text_short",
    "comment_text_full",
    "parent_text_full"
]

with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for interaction_type in [
        "pro_trump->pro_trump",
        "pro_kamala->pro_kamala",
        "pro_trump->pro_kamala",
        "pro_kamala->pro_trump"
    ]:
        for example in final_examples[interaction_type]:
            writer.writerow(example)


print("Done")
print(f"Created: {OUTPUT_CSV}")
print(f"Created: {OUTPUT_JSON}")

for interaction_type in [
    "pro_trump->pro_trump",
    "pro_kamala->pro_kamala",
    "pro_trump->pro_kamala",
    "pro_kamala->pro_trump"
]:
    print("\n" + "=" * 90)
    print(interaction_type)
    print("=" * 90)

    for ex in final_examples[interaction_type]:
        print(f"Score: {ex['score']}")
        print(f"Comment stance: {ex['comment_stance']}")
        print(f"Parent stance: {ex['parent_stance']}")
        print(f"Conflict: {ex['has_candidate_conflict']}")
        print(f"Comment: {ex['comment_text_short']}")
        print(f"Parent: {ex['parent_text_short']}")
        print("-" * 90)
import os
import json
import csv
import time
import zstandard as zstd
from collections import defaultdict

DATA_DIR = "data"

RC_FILE = os.path.join(DATA_DIR, "RC_2024-10.zst")
RS_FILE = os.path.join(DATA_DIR, "RS_2024-10.zst")

INTERACTIONS_CSV = os.path.join(DATA_DIR, "interactions_october_enriched.csv")
USERS_CSV = os.path.join(DATA_DIR, "users_final_side.csv")
SUMMARY_JSON = os.path.join(DATA_DIR, "summary_october.json")

MAX_ROWS = 1_000_000

LEFT_SUBS = {
    "politics",
    "democrats",
    "liberal",
    "progressive",
    "PoliticalDiscussion",
}

RIGHT_SUBS = {
    "Conservative",
    "Republican",
    "AskTrumpSupporters",
    "The_Donald",
}

INTERACTION_COLUMNS = [
    "post_id",
    "post_author",
    "post_subreddit",
    "post_side",
    "post_text",
    "comment_id",
    "comment_author",
    "comment_author_final_side",
    "comment_side_by_subreddit",
    "comment_body",
    "parent_type",
    "parent_id",
    "parent_author",               
    "parent_author_final_side",
    "parent_text",
    "interaction_side_subreddit",
    "interaction_side_final",
    "link_id",
    "comment_subreddit",
    "created_utc",
]

USER_COLUMNS = [
    "user",
    "left_count",
    "right_count",
    "final_side",
]


def get_side(subreddit):
    sub = (subreddit or "").strip()
    if sub in LEFT_SUBS:
        return "left"
    if sub in RIGHT_SUBS:
        return "right"
    return None


def clean_text(text):
    if text is None:
        return ""
    return str(text).replace("\n", " ").replace("\r", " ").strip()


def read_zst_lines(file_path):
    with open(file_path, "rb") as f:
        dctx = zstd.ZstdDecompressor(max_window_size=2147483648)
        with dctx.stream_reader(f) as reader:
            buffer = ""

            while True:
                chunk = reader.read(16384)
                if not chunk:
                    break

                buffer += chunk.decode("utf-8", errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        yield line

            if buffer.strip():
                yield buffer


def print_progress(label, checked, written=None, start_time=None):
    elapsed = time.time() - start_time if start_time else 0
    speed = checked / elapsed if elapsed > 0 else 0

    if written is None:
        print(
            f"{label}: checked={checked:,} | "
            f"speed={speed:,.0f} rows/sec | "
            f"time={elapsed / 60:.1f} min"
        )
    else:
        print(
            f"{label}: checked={checked:,} | written={written:,} | "
            f"speed={speed:,.0f} rows/sec | "
            f"time={elapsed / 60:.1f} min"
        )


def build_posts_table_and_user_votes():
    tracked_posts = {}
    user_votes = defaultdict(lambda: {"left": 0, "right": 0})

    total_posts = 0
    kept_posts = 0
    start_time = time.time()

    print("========== RS START ==========")

    for line in read_zst_lines(RS_FILE):
        total_posts += 1

        try:
            obj = json.loads(line)
        except Exception:
            continue

        post_id = obj.get("id", "")
        author = obj.get("author", "")
        subreddit = obj.get("subreddit", "")
        side = get_side(subreddit)

        if not post_id or not side:
            if total_posts % 1_000_000 == 0:
                print_progress("RS progress", total_posts, kept_posts, start_time)
            continue

        title = clean_text(obj.get("title", ""))
        selftext = clean_text(obj.get("selftext", ""))

        post_text = title
        if selftext:
            post_text = f"{title} || {selftext}" if title else selftext

        tracked_posts[post_id] = {
            "post_id": post_id,
            "post_author": author,
            "post_subreddit": subreddit,
            "post_side": side,
            "post_text": post_text,
        }

        if author and author != "[deleted]":
            user_votes[author][side] += 1

        kept_posts += 1

        if total_posts % 1_000_000 == 0:
            print_progress("RS progress", total_posts, kept_posts, start_time)

    print("\nFinished RS")
    print_progress("RS final", total_posts, kept_posts, start_time)

    return tracked_posts, user_votes


def collect_rc_user_votes(user_votes):
    total_comments = 0
    political_comments = 0
    start_time = time.time()

    print("\n========== RC VOTES PASS ==========")

    for line in read_zst_lines(RC_FILE):
        total_comments += 1

        try:
            obj = json.loads(line)
        except Exception:
            continue

        author = obj.get("author", "")
        subreddit = obj.get("subreddit", "")
        side = get_side(subreddit)

        if side and author and author != "[deleted]":
            user_votes[author][side] += 1
            political_comments += 1

        if total_comments % 1_000_000 == 0:
            print_progress("RC votes progress", total_comments, political_comments, start_time)

    print("\nFinished RC votes pass")
    print_progress("RC votes final", total_comments, political_comments, start_time)


def build_users_final_side(user_votes):
    final_users = {}
    left_users = 0
    right_users = 0
    unknown_users = 0

    print("\nBuilding users_final_side.csv...")

    with open(USERS_CSV, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=USER_COLUMNS)
        writer.writeheader()

        for user, votes in user_votes.items():
            left_count = votes["left"]
            right_count = votes["right"]

            if left_count > right_count:
                final_side = "left"
                left_users += 1
            elif right_count > left_count:
                final_side = "right"
                right_users += 1
            else:
                final_side = "unknown"
                unknown_users += 1

            final_users[user] = final_side

            writer.writerow({
                "user": user,
                "left_count": left_count,
                "right_count": right_count,
                "final_side": final_side,
            })

    print("Finished users_final_side.csv")
    print(f"Total users seen: {len(user_votes):,}")
    print(f"Left users: {left_users:,}")
    print(f"Right users: {right_users:,}")
    print(f"Unknown users: {unknown_users:,}")

    return final_users, {
        "classified_left_users": left_users,
        "classified_right_users": right_users,
        "unknown_or_tied_users": unknown_users,
        "total_users_seen": len(user_votes),
    }


def build_interactions_csv(tracked_posts, final_users):
    comment_author_map = {}
    comment_body_map = {}

    total_comments = 0
    written_rows = 0
    replies_to_posts = 0
    replies_to_comments = 0
    skipped_unknown_parent = 0
    start_time = time.time()

    print("\n========== RC INTERACTIONS PASS ==========")

    with open(INTERACTIONS_CSV, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=INTERACTION_COLUMNS)
        writer.writeheader()

        for line in read_zst_lines(RC_FILE):
            total_comments += 1

            if written_rows >= MAX_ROWS:
                print(f"\nReached {MAX_ROWS:,} rows. Stopping early.")
                break

            try:
                obj = json.loads(line)
            except Exception:
                if total_comments % 1_000_000 == 0:
                    print_progress("RC interactions progress", total_comments, written_rows, start_time)
                continue

            comment_id = obj.get("id", "")
            comment_author = obj.get("author", "")
            comment_subreddit = obj.get("subreddit", "")
            comment_side_by_subreddit = get_side(comment_subreddit)
            parent_id = obj.get("parent_id", "")
            link_id = obj.get("link_id", "")
            created_utc = obj.get("created_utc", "")
            comment_body = clean_text(obj.get("body", ""))

            if not comment_id:
                continue

            comment_author_map[comment_id] = comment_author
            comment_body_map[comment_id] = comment_body

            post_id_from_link = link_id.replace("t3_", "") if isinstance(link_id, str) else ""
            tracked_post = tracked_posts.get(post_id_from_link)

            if not tracked_post:
                if total_comments % 1_000_000 == 0:
                    print_progress("RC interactions progress", total_comments, written_rows, start_time)
                continue

            parent_type = ""
            parent_author = ""
            parent_text = ""

            if isinstance(parent_id, str) and parent_id.startswith("t3_"):
                parent_type = "post"
                parent_author = tracked_post["post_author"]
                parent_text = tracked_post["post_text"]
                replies_to_posts += 1

            elif isinstance(parent_id, str) and parent_id.startswith("t1_"):
                parent_type = "comment"
                parent_comment_id = parent_id.replace("t1_", "")
                parent_author = comment_author_map.get(parent_comment_id, "")
                parent_text = comment_body_map.get(parent_comment_id, "")

                if not parent_author:
                    skipped_unknown_parent += 1
                    if total_comments % 1_000_000 == 0:
                        print_progress("RC interactions progress", total_comments, written_rows, start_time)
                    continue

                replies_to_comments += 1

            else:
                if total_comments % 1_000_000 == 0:
                    print_progress("RC interactions progress", total_comments, written_rows, start_time)
                continue

            comment_author_final_side = final_users.get(comment_author, "unknown")
            parent_author_final_side = final_users.get(parent_author, "unknown")

            interaction_side_subreddit = ""
            if comment_side_by_subreddit and tracked_post["post_side"]:
                interaction_side_subreddit = f"{comment_side_by_subreddit}->{tracked_post['post_side']}"

            interaction_side_final = ""
            if comment_author_final_side != "unknown" and parent_author_final_side != "unknown":
                interaction_side_final = f"{comment_author_final_side}->{parent_author_final_side}"

            row = {
                "post_id": tracked_post["post_id"],
                "post_author": tracked_post["post_author"],      # כותב הפוסט
                "post_subreddit": tracked_post["post_subreddit"],
                "post_side": tracked_post["post_side"],
                "post_text": tracked_post["post_text"],
                "comment_id": comment_id,
                "comment_author": comment_author,                # כותב התגובה
                "comment_author_final_side": comment_author_final_side,
                "comment_side_by_subreddit": comment_side_by_subreddit or "",
                "comment_body": comment_body,
                "parent_type": parent_type,
                "parent_id": parent_id,
                "parent_author": parent_author,
                "parent_author_final_side": parent_author_final_side,
                "parent_text": parent_text,
                "interaction_side_subreddit": interaction_side_subreddit,
                "interaction_side_final": interaction_side_final,
                "link_id": link_id,
                "comment_subreddit": comment_subreddit,
                "created_utc": created_utc,
            }

            writer.writerow(row)
            written_rows += 1

            if total_comments % 1_000_000 == 0:
                print_progress("RC interactions progress", total_comments, written_rows, start_time)

    print("\nFinished RC interactions pass")
    print_progress("RC interactions final", total_comments, written_rows, start_time)
    print(f"Replies to posts: {replies_to_posts:,}")
    print(f"Replies to comments: {replies_to_comments:,}")
    print(f"Skipped unknown parent author: {skipped_unknown_parent:,}")

    return {
        "total_comments_checked": total_comments,
        "interaction_rows_written": written_rows,
        "replies_to_posts": replies_to_posts,
        "replies_to_comments": replies_to_comments,
        "skipped_unknown_parent_author": skipped_unknown_parent,
        "row_limit": MAX_ROWS,
    }


def analyze_echo_chamber_from_csv():
    print("\nAnalyzing echo chamber from CSV...")

    counts = {
        "left_to_left": 0,
        "left_to_right": 0,
        "right_to_left": 0,
        "right_to_right": 0,
        "unknown": 0,
    }

    rows_analyzed = 0

    with open(INTERACTIONS_CSV, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            rows_analyzed += 1
            interaction_side = (row.get("interaction_side_final") or "").strip()

            if interaction_side == "left->left":
                counts["left_to_left"] += 1
            elif interaction_side == "left->right":
                counts["left_to_right"] += 1
            elif interaction_side == "right->left":
                counts["right_to_left"] += 1
            elif interaction_side == "right->right":
                counts["right_to_right"] += 1
            else:
                counts["unknown"] += 1

    within = counts["left_to_left"] + counts["right_to_right"]
    cross = counts["left_to_right"] + counts["right_to_left"]
    total_known = within + cross
    ratio = round(within / total_known, 4) if total_known > 0 else 0

    if ratio > 0.7:
        classification = "Strong Echo Chamber"
    elif ratio > 0.6:
        classification = "Moderate Echo Chamber"
    else:
        classification = "Weak / No Echo Chamber"

    return {
        "rows_analyzed": rows_analyzed,
        "interaction_types": counts,
        "within_group": within,
        "cross_group": cross,
        "homophily_ratio": ratio,
        "classification": classification,
    }


def save_summary_json(posts_count, rc_stats, user_stats, echo_stats):
    summary = {
        "month": "2024-10",
        "posts": {
            "political_posts_kept": posts_count,
        },
        "interactions": rc_stats,
        "users": user_stats,
        "echo_chamber": echo_stats,
        "output_files": {
            "interactions_csv": INTERACTIONS_CSV,
            "users_csv": USERS_CSV,
            "summary_json": SUMMARY_JSON,
        }
    }

    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("\nSummary:")
    print(json.dumps(summary, indent=4))


if __name__ == "__main__":
    overall_start = time.time()

    tracked_posts, user_votes = build_posts_table_and_user_votes()
    collect_rc_user_votes(user_votes)
    final_users, user_stats = build_users_final_side(user_votes)
    rc_stats = build_interactions_csv(tracked_posts, final_users)
    echo_stats = analyze_echo_chamber_from_csv()
    save_summary_json(len(tracked_posts), rc_stats, user_stats, echo_stats)

    total_elapsed = time.time() - overall_start

    print("\nFiles created:")
    print(f"- {INTERACTIONS_CSV}")
    print(f"- {USERS_CSV}")
    print(f"- {SUMMARY_JSON}")
    print(f"\nTotal runtime: {total_elapsed / 60:.1f} minutes")
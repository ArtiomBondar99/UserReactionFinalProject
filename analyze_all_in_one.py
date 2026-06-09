import csv
import os
from collections import Counter
import matplotlib.pyplot as plt

INPUT_FILE = "data/interactions_final_unique_users.csv"
OUTPUT_DIR = "results_final"

os.makedirs(OUTPUT_DIR, exist_ok=True)

counts = Counter()

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        interaction = (row.get("user_interaction_side") or "").strip()
        if interaction:
            counts[interaction] += 1

left_left = counts["left->left"]
right_right = counts["right->right"]
left_right = counts["left->right"]
right_left = counts["right->left"]

values = [left_left, right_right, left_right, right_left]
labels = ["Left → Left", "Right → Right", "Left → Right", "Right → Left"]
colors = ["#2F80ED", "#EB5757", "#F2994A", "#27AE60"]

total = sum(values)

within = left_left + right_right
cross = left_right + right_left

within_pct = round((within / total) * 100) if total else 0
cross_pct = round((cross / total) * 100) if total else 0

print("\n===== RESULTS =====")
print(f"Left → Left: {left_left:,}")
print(f"Right → Right: {right_right:,}")
print(f"Left → Right: {left_right:,}")
print(f"Right → Left: {right_left:,}")
print(f"Total: {total:,}")
print(f"Within: {within:,} ({within_pct}%)")
print(f"Cross: {cross:,} ({cross_pct}%)")


# =========================
# 1. Table PNG
# =========================
fig, ax = plt.subplots(figsize=(8, 5), facecolor="white")
ax.axis("off")

table_data = [
    ["Left → Left", f"{left_left:,}"],
    ["Right → Right", f"{right_right:,}"],
    ["Left → Right", f"{left_right:,}"],
    ["Right → Left", f"{right_left:,}"],
    ["Total Interactions", f"{total:,}"],
]

table = ax.table(
    cellText=table_data,
    colLabels=["Interaction Types", "Count"],
    loc="center",
    cellLoc="center",
    colLoc="center",
    colWidths=[0.6, 0.4]
)

table.auto_set_font_size(False)
table.set_fontsize(16)
table.scale(1.4, 2.5)

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#D0D7DE")
    cell.set_linewidth(1.2)

    if row == 0:
        cell.set_facecolor("#EAF0F6")
        cell.set_text_props(weight="bold")

    if row == 5:
        cell.set_facecolor("#EAF0F6")
        cell.set_text_props(weight="bold")

for i, color in enumerate(colors, start=1):
    table[(i, 1)].get_text().set_color(color)
    table[(i, 1)].get_text().set_weight("bold")

plt.title("Interaction Types", fontsize=18, fontweight="bold", pad=20)

plt.savefig(
    os.path.join(OUTPUT_DIR, "table_unique.png"),
    dpi=600,
    bbox_inches="tight",
    facecolor="white"
)

plt.close()


# =========================
# 2. Pie PNG
# =========================
def autopct_format(pct):
    return f"{pct:.0f}%" if pct >= 2 else ""


fig, ax = plt.subplots(figsize=(8, 8), facecolor="white")

wedges, texts, autotexts = ax.pie(
    values,
    colors=colors,
    autopct=autopct_format,
    startangle=90,
    counterclock=False,
    pctdistance=0.72,
    textprops={"fontsize": 16, "fontweight": "bold"},
    wedgeprops={"linewidth": 1.2, "edgecolor": "white"}
)

for autotext in autotexts:
    autotext.set_color("white")

ax.legend(
    wedges,
    labels,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.15),
    ncol=2,
    fontsize=12,
    frameon=False
)

ax.set_title("Interaction Distribution", fontsize=18, fontweight="bold", pad=20)

plt.savefig(
    os.path.join(OUTPUT_DIR, "pie_unique.png"),
    dpi=600,
    bbox_inches="tight",
    facecolor="white"
)

plt.close()


# =========================
# 3. Within vs Cross Poster Style PNG
# =========================
fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")

bars = ax.bar(
    ["WITHIN GROUP", "CROSS GROUP"],
    [within, cross],
    color=["#2F80ED", "#EB5757"],
    width=0.6
)

max_value = max(within, cross) if max(within, cross) else 1
ax.set_ylim(0, max_value * 1.35)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

for bar, value, pct in zip(bars, [within, cross], [within_pct, cross_pct]):
    x = bar.get_x() + bar.get_width() / 2

    ax.text(
        x,
        value + (max_value * 0.065),
        f"{value:,}",
        ha="center",
        va="bottom",
        fontsize=18,
        fontweight="bold",
        color="#111827"
    )

    ax.text(
        x,
        value + (max_value * 0.025),
        f"{pct}%",
        ha="center",
        va="bottom",
        fontsize=15,
        fontweight="bold",
        color="#374151"
    )

ax.set_title(
    "WITHIN vs CROSS INTERACTIONS",
    fontsize=20,
    fontweight="bold",
    pad=25
)

ax.set_ylabel("Number of Connections", fontsize=13)
ax.tick_params(axis="x", labelsize=12)
ax.tick_params(axis="y", labelsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.3)

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "within_cross_poster.png"),
    dpi=600,
    bbox_inches="tight",
    facecolor="white"
)

plt.close()

print("\nCreated files:")
print("results_final/table_unique.png")
print("results_final/pie_unique.png")
print("results_final/within_cross_poster.png")
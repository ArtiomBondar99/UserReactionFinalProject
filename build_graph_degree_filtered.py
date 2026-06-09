import csv
import networkx as nx

INPUT_FILE = "data/interactions_final_unique_users.csv"
OUTPUT_FILE = "data/graph_unique_users.graphml"

G = nx.DiGraph()

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        source = (row.get("comment_author") or "").strip()
        target = (row.get("parent_author") or "").strip()

        source_side = (row.get("source_user_side") or "").strip()
        target_side = (row.get("target_user_side") or "").strip()

        if not source or not target:
            continue

        if source == "[deleted]" or target == "[deleted]":
            continue

        # Add source node
        if source not in G:
            G.add_node(source, side=source_side)

        # Add target node
        if target not in G:
            G.add_node(target, side=target_side)

        # Since this is the unique file, each pair should appear once
        if G.has_edge(source, target):
            G[source][target]["weight"] += 1
        else:
            G.add_edge(source, target, weight=1)

nx.write_graphml(G, OUTPUT_FILE)

print("Done")
print(f"Graph created: {OUTPUT_FILE}")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
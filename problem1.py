import networkx as nx
import matplotlib.pyplot as plt
import itertools
import gurobipy as gp
from gurobipy import *
locations = {
    "Bunker": (0, 100),
    "Grocers1": (200, 600),
    "Pharmacy": (450, 600),
    "Hospital": (550, 400),
    "Grocery2": (950, 400),
    "GasStation": (450, 200),
    "A": (0,0),
    "B": (0,200),
    "C": (200, 0),
    "D": (200, 200),
    "E": (200, 400),
    "F": (200, 500),
    "G": (200, 700),
    "H": (450, 0),
    "I": (450, 400),
    "J": (450, 500),
    "K": (450, 700),
    "L": (650, 0),
    "M": (650, 400),
    "N": (650, 600),
    "O": (650, 700),
    "P": (950, 600)
}
# Edges to be added to the graph, specified as pairs of node names
edges = [
    ("Bunker", "A"),
    ("Bunker", "B"),
    ("A", "C"),
    ("B", "D"),
    ("C", "D"),
    ("C", "H"),
    ("D", "E"),
    ("E", "I"),
    ("E", "F"),
    ("F", "J"),
    ("F", "Grocers1"),
    ("Grocers1", "G"),
    ("G", "K"),
    ("K", "O"),
    ("K","Pharmacy"),
    ("Pharmacy", "N"),
    ("Pharmacy", "J"),
    ("J", "I"),
    ("Hospital", "M"),
    ("I", "Hospital"),
    ("I", "GasStation"),
    ("GasStation", "H"),
    ("H", "L"),
    ("L", "M"),
    ("M", "Grocery2"),
    ("Grocery2", "P"),
    ("P", "N"),
    ("N", "M"),
    ("N", "O")
]

# Create a graph
G = nx.Graph()

# Add nodes with positions
for node, pos in locations.items():
    G.add_node(node, pos=pos)

# Adding specified edges to the graph
G.add_edges_from(edges)

# Extract positions for nodes from the graph
pos = nx.get_node_attributes(G, 'pos')

# Draw the network
nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=9, font_color='black')
plt.title('Map of the Town')
plt.show()
#List of nodes
nodes = list(locations.keys())

#Number of nodes
num_nodes = len(locations)

# Set of required nodes
required_nodes = {"Bunker", "Grocers1", "Pharmacy", "GasStation", "Hospital"}
non_required_nodes = set(nodes) - set(required_nodes)

#All edges
all_edges = edges + [(b, a) for a, b in edges]

# Filter edges to include only those with at least one node in required_nodes
required_edges = [edge for edge in all_edges if edge[0] in required_nodes or edge[1] in required_nodes]
all_required_edges = required_edges + [(b, a) for a, b in required_edges]

# Filter edges to include only those where neither endpoint is in required_nodes
non_required_edges = [edge for edge in all_edges if edge[0] not in required_nodes and edge[1] not in required_nodes]
all_non_required_edges = non_required_edges + [(b, a) for a, b in non_required_edges]

# Display the filtered edges
# print( f"These are the required edges: {all_required_edges}")
# print( f"These are the non-required edges: {all_non_required_edges}")

#Distance between nodes
dist = {(i, j): abs(pos[i][0] - pos[j][0]) + abs(pos[i][1] - pos[j][1]) for i, j in all_edges}

#add dummy node
locations["dummy_bunker"] = (-100, 100)
edges.append(("Bunker", "dummy_bunker"))

G = nx.Graph()
for u, v in edges:
    w = abs(locations[u][0]-locations[v][0]) + abs(locations[u][1]-locations[v][1])
    G.add_edge(u, v, weight=w)

# -----------------------
start, end = "Bunker", "dummy_bunker"
must_visit = ["Pharmacy", "Hospital", "GasStation"]
grocers = ["Grocers1", "Grocery2"]

best_total = float("inf")
best_path = None
best_grocer = None

for g in grocers:
    visit_nodes = must_visit + [g]
    for perm in itertools.permutations(visit_nodes):
        total = 0
        full_path = [start]
        feasible = True
        for a, b in zip([start] + list(perm), list(perm) + [end]):
            try:
                sub = nx.shortest_path(G, a, b, weight="weight")
                length = nx.shortest_path_length(G, a, b, weight="weight")
                total += length
                full_path += sub[1:]
            except nx.NetworkXNoPath:
                feasible = False
                break

        if feasible:
            unique_nodes = len(set(full_path))
            # find same distance but less node positions
            if (total < best_total) or (total == best_total and unique_nodes < len(set(best_path))):
                best_total = total
                best_path = full_path
                best_grocer = g

# =====================
pos = {k: v for k, v in locations.items()}
plt.figure(figsize=(11,8))
nx.draw(G, pos, with_labels=True, node_color='lightgray', node_size=600, font_size=8)
nx.draw_networkx_nodes(G, pos, nodelist=best_path, node_color='orange', node_size=700)
path_edges = list(zip(best_path, best_path[1:]))
nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3)
edge_labels = { (u, v): f"{G[u][v]['weight']}" for (u, v) in G.edges }
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, label_pos=0.5, font_color='gray')

for idx, node in enumerate(best_path):
    x, y = pos[node]
    plt.text(x, y+25, f"{idx+1}", fontsize=9, ha='center', color='black')

plt.title(f"最优生存路线（经 {best_grocer}，总距离 {best_total:.0f}）", fontsize=13)
plt.show()
"""Case Study 10 — GNN by Hand (Python track).

The case study lab walked you through a hand-computed forward pass.
Here we do it in pure numpy on the same 6-node toy network. No
torch, no torch_geometric. Just the math.

Step by step:
  1. Build the adjacency matrix (with self-loops).
  2. Symmetric-normalize it (D^{-1/2} A D^{-1/2}).
  3. Apply a single GCN layer: H = ReLU(A_norm @ X @ W).
  4. Stack a second layer.
  5. Read off the embedding for the bottleneck node (node 4).

Then we run the same pipeline on a 200-node project-scale network so
you can see GNN embeddings at non-toy scale.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# Pure numpy + pandas. No torch — we want you to *see* the matrix math.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# All the building blocks live in functions.py: tiny + large data
# loaders, adjacency builder, the symmetric normalization, ReLU, and
# the GCN layer itself. Read them once — each is 5-10 lines.
from functions import (
    load_tiny, load_large, adjacency, normalize, relu, gcn_layer,
)

print("\n🚀 Case Study 10 — GNN by Hand (Python)")
print("   Two-layer GCN, no torch. Pure numpy on a 6-node + 200-node network.\n")

## 0.3 Load data #############################################################

nodes, edges = load_tiny()
print(nodes)
print(edges)
print(f"✅ Loaded tiny network: {len(nodes)} nodes, {len(edges)} edges.")


# 1. Adjacency and normalization #############################################
#
# Self-loops let each node "send a message to itself" so its own
# features survive into the next layer. Symmetric normalization
# D^{-1/2} A D^{-1/2} stops high-degree nodes from dominating their
# neighbors. These two preprocessing tricks are the heart of a GCN.

A = adjacency(nodes, edges, add_self_loops=True)
print("A (with self-loops):")
print(A.astype(int))

A_norm = normalize(A)
print("A_norm (symmetric-normalized):")
print(A_norm.round(3))


# 2. Feature matrix and weight matrices ######################################
#
# Each node has 2 input features: (daily_output, defect_rate).
# Layer 1 maps 2 -> 3 hidden dims; layer 2 maps 3 -> 3.

X = nodes[["daily_output", "defect_rate"]].to_numpy()
print("X (input features):")
print(X)

# Fixed weights for reproducibility. In a real GNN these are learned
# via gradient descent on an objective; here we hard-code them so the
# whole pipeline is one numpy matmul chain.
W1 = np.array([
    [ 0.5, -0.2,  0.8],
    [-0.7,  0.4,  0.3],
])
W2 = np.array([
    [ 0.6,  0.1, -0.4],
    [ 0.2,  0.7,  0.3],
    [-0.5,  0.4,  0.6],
])


# 3. Forward pass ############################################################
#
# H_{l+1} = activation(A_norm @ H_l @ W_l). The activation is ReLU.

H1 = gcn_layer(A_norm, X,  W1, activation="relu")
print("H1 (after layer 1, ReLU):")
print(H1.round(4))

H2 = gcn_layer(A_norm, H1, W2, activation="relu")
print("H2 (after layer 2, ReLU):")
print(H2.round(4))


# 4. What does node 4 (the bottleneck) end up looking like? ##################
#
# Node 4 sits between two clusters in our 6-node toy. After two GCN
# layers its embedding has absorbed features from both sides.

print("Final embedding for node 4 (the bottleneck):")
print(H2[4].round(4))
print(f"🧪 Node 4 embedding norm: {np.linalg.norm(H2[4]):.4f}")


# 5. The same pipeline on a 200-node project-scale network ###################

ln, le = load_large()
A_l = normalize(adjacency(ln, le, add_self_loops=True))
X_l = ln[["daily_output", "defect_rate"]].to_numpy()

H1_l = gcn_layer(A_l, X_l, W1, activation="relu")
H2_l = gcn_layer(A_l, H1_l, W2, activation="relu")
print(f"📊 Large network embedding shape: {H2_l.shape}")

# Plot the first two embedding dimensions, colored by node id, so we
# can see whether the bottlenecks (every 25th node) cluster separately.
fig, ax = plt.subplots(figsize=(7, 5))
is_bot = ln["node_id"].isin([25 * i for i in range(1, 8)]).to_numpy()
ax.scatter(H2_l[~is_bot, 0], H2_l[~is_bot, 1], s=12, alpha=0.5,
           c="#999", label="regular nodes")
ax.scatter(H2_l[is_bot, 0], H2_l[is_bot, 1], s=80, c="#d62728",
           edgecolor="white", label="planted bottlenecks")
ax.set_xlabel("embedding dim 0")
ax.set_ylabel("embedding dim 1")
ax.set_title("After 2 GCN layers, do bottlenecks separate?")
ax.legend()
fig.tight_layout()
fig.savefig("gnn_embeddings.png", dpi=120)
plt.close(fig)
print("💾 Saved gnn_embeddings.png")


# 6. Learning Check ##########################################################
#
# QUESTION: With the layer weights W1 and W2 defined above (symmetric
# normalization, ReLU, self-loops), what is the FINAL embedding (3
# numbers) for node 4 on the tiny network?
#
# Round each to 4 decimal places. Submit as a comma-separated string.

emb = H2[4].round(4)
answer = ", ".join(f"{v:.4f}" for v in emb)

print(f"\n📝 Learning Check answer: {answer}")

print("\n🎉 Done. Move on to the case study report when you're ready.")

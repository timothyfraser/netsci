// Shared between the normal and print-resolution capture scripts.
const RED_CANVAS = new Set(['stagered']);
const plotCode = (theme) => {
  const cornell = theme !== 'orig';
  const redCanvas = RED_CANVAS.has(theme);
  const face = redCanvas ? '#C32529' : '#FFFFFF';
  const ink = redCanvas ? '#FFFFFF' : '#222222';
  const edge = redCanvas ? '#F0C8C8' : '#c9c9c9';
  const cmap = !cornell ? '"plasma"'
    : redCanvas
      ? 'LinearSegmentedColormap.from_list("c", ["#FFFFFF", "#FFE9A8", "#F7C948", "#8C1515"])'
      : 'LinearSegmentedColormap.from_list("c", ["#C4C4C4", "#E4A11B", "#B31B1B", "#6E0F0F"])';
  return `# Power grid — which buses actually carry the load?
import pandas as pd, networkx as nx
import matplotlib.pyplot as plt

nodes = pd.read_csv("power-grid-nodes.csv")
edges = pd.read_csv("power-grid-edges.csv")
G = nx.from_pandas_edgelist(edges, source="from_id", target="to_id")
print("Nodes:", G.number_of_nodes(), " Edges:", G.number_of_edges())

bet = nx.betweenness_centrality(G)
print("Most critical:", sorted(bet, key=bet.get, reverse=True)[:5])
${cornell ? 'from matplotlib.colors import LinearSegmentedColormap' : ''}
CMAP = ${cmap}
plt.rcParams.update({"font.size": 15, "axes.titlesize": 19, "text.color": "${ink}"})
pos = nx.spring_layout(G, seed=42)
fig = plt.figure(figsize=(6.4, 4.8), facecolor="${face}")
fig.gca().set_facecolor("${face}")
nx.draw_networkx_edges(G, pos, edge_color="${edge}", width=0.8)
nx.draw_networkx_nodes(G, pos, node_color=[bet[n] for n in G.nodes], cmap=CMAP,
                       node_size=[1400 * bet[n] + 16 for n in G.nodes], linewidths=0)
plt.title("Power grid — size & color = betweenness", color="${ink}")
plt.axis("off"); plt.tight_layout(); plt.show()
`;
};

module.exports = { plotCodeFor: plotCode };

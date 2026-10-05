"""Interactive (plotly) version of the 朱元璋 co-occurrence network.

Uses the same graph as network.py but renders an HTML page that can be
zoomed, panned and hovered.

Run from the repository root:  python plot_html.py
"""
import networkx as nx
import plotly.graph_objects as go

from network import build_graph, NAME2GROUP, GROUP_COLOR, TARGET

OUT = "output/zhuyuanzhang_network.html"


def main():
    G, person_count, names = build_graph()
    pos = nx.spring_layout(G, k=1.1, seed=7, iterations=300)

    fig = go.Figure()

    # edges (one trace per distinct weight so line width can vary)
    weights = sorted({d["weight"] for _, _, d in G.edges(data=True)})
    for w in weights:
        xs, ys, texts = [], [], []
        for u, v, d in G.edges(data=True):
            if d["weight"] != w:
                continue
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            xs += [x0, x1, None]
            ys += [y0, y1, None]
            texts.append(f"{u} – {v}: {w}")
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", hoverinfo="text",
            line=dict(width=0.6 + 0.5 * w, color="#999"),
            text="", name=f"weight {w}"))

    # nodes
    node_x, node_y, node_text, node_color, node_size, hover = [], [], [], [], [], []
    for n in G.nodes:
        x, y = pos[n]
        node_x.append(x); node_y.append(y)
        node_text.append(n)
        if n == TARGET:
            node_color.append("#c0392b"); node_size.append(45)
            hover.append(f"<b>{n}</b> (朱元璋)")
        else:
            g = NAME2GROUP.get(n, "其他")
            node_color.append(GROUP_COLOR.get(g, "#34495e"))
            node_size.append(12 + 1.6 * G.nodes[n]["freq"])
            hover.append(f"<b>{n}</b><br>阵营: {g}<br>与太祖共现: "
                         f"{G.nodes[n]['freq']} 次")
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers+text", text=node_text,
        textposition="top center", textfont=dict(size=12),
        hovertext=hover, hoverinfo="text",
        marker=dict(color=node_color, size=node_size,
                    line=dict(color="white", width=1)),
        name="人物"))

    fig.update_layout(
        title="Co-occurrence network around 太祖 (朱元璋) in the Mingshi "
              "— interactive",
        showlegend=True, hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white", height=850,
        margin=dict(l=20, r=20, t=70, b=20),
    )
    fig.write_html(OUT, include_plotlyjs="cdn")
    print(f"wrote {OUT}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")


if __name__ == "__main__":
    main()

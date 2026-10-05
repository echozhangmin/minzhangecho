"""Co-occurrence network of people around 太祖 (Zhu Yuanzhang) in the Mingshi.

For every sentence containing 太祖, the script detects a curated list of
Yuan-Ming transition figures (canonical name + common short forms) and counts
how often each person co-occurs with 太祖, and how often two people appear in
the same 太祖 sentence. The result is drawn as a network and saved as
output/zhuyuanzhang_network.png.

Run from the repository root:  python network.py
"""
import os
from collections import Counter
from itertools import combinations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

matplotlib.rcParams["font.sans-serif"] = [
    "Arial Unicode MS", "Songti SC", "PingFang SC", "Heiti SC", "STSong",
    "Noto Sans CJK SC", "SimHei", "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False

SEGMENTED = "data/mingshi_segmented.txt"
OUT = "output/zhuyuanzhang_network.png"
TARGET = "太祖"

# canonical name -> aliases (short forms the text also uses)
ALIASES = {
    "陈友谅": ["陈友谅", "友谅"], "张士诚": ["张士诚", "士诚"], "宋濂": ["宋濂"],
    "徐达": ["徐达"], "刘基": ["刘基", "伯温"], "郭子兴": ["郭子兴", "子兴"],
    "常遇春": ["常遇春"], "李善长": ["李善长"], "张定边": ["张定边", "定边"],
    "李文忠": ["李文忠", "文忠"], "韩林儿": ["韩林儿", "林儿"], "廖永忠": ["廖永忠"],
    "张昶": ["张昶"], "康茂才": ["康茂才", "茂才"], "陈友定": ["陈友定", "友定"],
    "胡惟庸": ["胡惟庸"], "方国珍": ["方国珍", "国珍"], "叶琛": ["叶琛"],
    "邓愈": ["邓愈"], "胡大海": ["胡大海"], "汪广洋": ["汪广洋"], "杨宪": ["杨宪"],
    "傅友德": ["傅友德"], "耿炳文": ["耿炳文", "炳文"], "章溢": ["章溢"],
    "李思齐": ["李思齐", "思齐"], "花云": ["花云"], "朱升": ["朱升"],
    "朱亮祖": ["朱亮祖", "亮祖"], "冯胜": ["冯胜"], "汤和": ["汤和"],
    "蓝玉": ["蓝玉"], "沐英": ["沐英"], "王保保": ["王保保", "保保", "扩廓"],
}
TOKEN2NAME = {a: c for c, als in ALIASES.items() for a in als}

# adversaries (red) vs supporters/others (blue) — for colouring
ADVERSARIES = {"陈友谅", "张士诚", "张定边", "韩林儿", "陈友定", "方国珍",
               "李思齐", "王保保"}


def main():
    lines = open(SEGMENTED, encoding="utf-8").read().splitlines()

    person_count = Counter()          # person co-occurring with 太祖
    pair_count = Counter()            # two persons in the same 太祖 sentence
    for line in lines:
        tokens = set(line.split())
        if TARGET not in tokens:
            continue
        present = {TOKEN2NAME[t] for t in tokens if t in TOKEN2NAME}
        for name in present:
            person_count[name] += 1
        for a, b in combinations(sorted(present), 2):
            pair_count[(a, b)] += 1

    MIN_FREQ = 2
    names = [n for n, c in person_count.most_common() if c >= MIN_FREQ]

    G = nx.Graph()
    G.add_node(TARGET)
    for n in names:
        G.add_node(n, freq=person_count[n])
        G.add_edge(TARGET, n, weight=person_count[n])
    for (a, b), w in pair_count.items():
        if a in names and b in names and w >= 2:
            G.add_edge(a, b, weight=w)

    # ---- draw ----
    fig, ax = plt.subplots(figsize=(14, 11))
    pos = nx.spring_layout(G, k=0.9, seed=42, iterations=200)

    center = [TARGET]
    adversaries = [n for n in G.nodes if n in ADVERSARIES]
    others = [n for n in G.nodes if n != TARGET and n not in ADVERSARIES]

    nx.draw_networkx_edges(G, pos, ax=ax, width=[0.4 + 0.12 * G[u][v]["weight"]
                            for u, v in G.edges], alpha=0.35, edge_color="#888")
    nx.draw_networkx_nodes(G, pos, nodelist=center, node_color="#c0392b",
                           node_size=2600, ax=ax, edgecolors="white")
    nx.draw_networkx_nodes(G, pos, nodelist=others, node_color="#2c7fb8",
                           node_size=[600 + 90 * G.nodes[n]["freq"] for n in others],
                           ax=ax, edgecolors="white")
    nx.draw_networkx_nodes(G, pos, nodelist=adversaries, node_color="#e67e22",
                           node_size=[600 + 90 * G.nodes[n]["freq"] for n in adversaries],
                           ax=ax, edgecolors="white")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11)

    ax.set_title("Co-occurrence network around 太祖 (朱元璋) in the Mingshi\n"
                 "red = 太祖, orange = adversaries, blue = supporters/others; "
                 "node size = co-occurrence with 太祖", fontsize=13)
    ax.axis("off")
    os.makedirs("output", exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=200)
    print(f"wrote {OUT}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print("top persons:", ", ".join(f"{n}({person_count[n]})"
                                    for n in names[:15]))


if __name__ == "__main__":
    main()

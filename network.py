"""Co-occurrence network of people around 太祖 (Zhu Yuanzhang) in the Mingshi.

For every sentence containing 太祖, the script detects a curated list of
Yuan-Ming transition figures (canonical name + common short forms), counts how
often each person co-occurs with 太祖 and how often two people appear in the
same 太祖 sentence, then draws a network grouped by faction.

Outputs:
  output/zhuyuanzhang_network.png        the network figure
  output/zhuyuanzhang_network_edges.csv  node-node-weight edge list

Run from the repository root:  python network.py
(For the interactive version, run: python plot_html.py)
"""
import csv
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
OUT_PNG = "output/zhuyuanzhang_network.png"
OUT_CSV = "output/zhuyuanzhang_network_edges.csv"
TARGET = "太祖"

# ---- curated people, grouped by camp ----
GROUPS = {
    "群雄/对手": ["陈友谅", "张士诚", "张定边", "韩林儿", "刘福通", "陈友定",
                 "方国珍", "李思齐", "王保保", "明玉珍", "何真", "张良弼",
                 "徐寿辉", "赵普胜", "彭莹玉"],
    "开国名将": ["徐达", "常遇春", "汤和", "李文忠", "冯胜", "傅友德", "沐英",
                 "邓愈", "廖永忠", "胡大海", "耿炳文", "康茂才", "花云",
                 "朱亮祖", "吴良", "吴祯", "华云龙", "顾时", "陈德", "王志",
                 "薛显", "梅思祖", "黄彬", "赵德胜", "丁德兴", "陆仲亨",
                 "唐胜宗", "费聚", "周德兴", "谢再兴", "邵荣", "孙兴祖",
                 "曹良臣", "廖永安", "俞通海", "郭英"],
    "文臣谋士": ["刘基", "李善长", "宋濂", "章溢", "叶琛", "朱升", "陶安",
                 "汪广洋", "杨宪", "张昶", "胡惟庸", "陈宁", "涂节",
                 "刘三吾", "乐韶凤", "宋讷", "詹同", "陶凯", "陈遇",
                 "秦从龙", "王袆", "苏伯衡", "高启"],
    "皇亲宗室": ["马皇后", "朱标", "朱棣", "朱允炆", "朱樉", "朱棡", "朱橚",
                 "朱文正"],
    "元朝": ["脱脱", "纳哈出", "把匝剌瓦尔密"],
    "早年恩主": ["郭子兴"],
}
GROUP_COLOR = {
    "群雄/对手": "#e67e22",
    "开国名将": "#2c7fb8",
    "文臣谋士": "#27ae60",
    "皇亲宗室": "#8e44ad",
    "元朝": "#7f8c8d",
    "早年恩主": "#c0392b",
}
SHORT = {
    "陈友谅": ["友谅"], "张士诚": ["士诚"], "郭子兴": ["子兴"], "李文忠": ["文忠"],
    "韩林儿": ["林儿"], "刘福通": ["福通"], "张定边": ["定边"], "方国珍": ["国珍"],
    "刘基": ["伯温"], "王保保": ["保保", "扩廓"], "明玉珍": ["玉珍"],
    "李思齐": ["思齐"], "陈友定": ["友定"], "张良弼": ["良弼"], "耿炳文": ["炳文"],
    "康茂才": ["茂才"], "朱亮祖": ["亮祖"], "徐寿辉": ["寿辉"], "赵普胜": ["普胜"],
    "彭莹玉": ["莹玉"],
}
NAME2GROUP = {n: g for g, ns in GROUPS.items() for n in ns}
ALIASES = {n: [n] + SHORT.get(n, []) for n in NAME2GROUP}
TOKEN2NAME = {a: n for n, als in ALIASES.items() for a in als}


def build_graph(min_freq=2, min_pair=2):
    """Return (graph, person_count, names) built from the segmented corpus."""
    lines = open(SEGMENTED, encoding="utf-8").read().splitlines()

    person_count = Counter()
    pair_count = Counter()
    for line in lines:
        tokens = set(line.split())
        if TARGET not in tokens:
            continue
        present = {TOKEN2NAME[t] for t in tokens if t in TOKEN2NAME}
        for name in present:
            person_count[name] += 1
        for a, b in combinations(sorted(present), 2):
            pair_count[(a, b)] += 1

    names = [n for n, c in person_count.most_common() if c >= min_freq]
    G = nx.Graph()
    G.add_node(TARGET, freq=person_count.get(TARGET, 1))
    for n in names:
        G.add_node(n, freq=person_count[n])
        G.add_edge(TARGET, n, weight=person_count[n])
    for (a, b), w in pair_count.items():
        if a in names and b in names and w >= min_pair:
            G.add_edge(a, b, weight=w)
    return G, person_count, names


def draw_png(G, person_count, names):
    fig, ax = plt.subplots(figsize=(16, 12))
    pos = nx.spring_layout(G, k=1.1, seed=7, iterations=300)
    nx.draw_networkx_edges(G, pos, ax=ax, width=[0.3 + 0.10 * G[u][v]["weight"]
                            for u, v in G.edges], alpha=0.3, edge_color="#999")
    nx.draw_networkx_nodes(G, pos, nodelist=[TARGET], node_color="#c0392b",
                           node_size=3200, ax=ax, edgecolors="white")
    for group, color in GROUP_COLOR.items():
        nodes = [n for n in G.nodes if NAME2GROUP.get(n) == group]
        if not nodes:
            continue
        nx.draw_networkx_nodes(
            G, pos, nodelist=nodes, node_color=color,
            node_size=[500 + 80 * G.nodes[n]["freq"] for n in nodes],
            ax=ax, edgecolors="white", label=group)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11)
    ax.set_title("Co-occurrence network around 太祖 (朱元璋) in the Mingshi\n"
                 "node size = co-occurrence with 太祖; edge = same-sentence co-occurrence",
                 fontsize=14)
    ax.legend(scatterpoints=1, loc="upper left", fontsize=11, framealpha=0.9)
    ax.axis("off")
    os.makedirs("output", exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight")


def main():
    G, person_count, names = build_graph()
    draw_png(G, person_count, names)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "weight"])
        for u, v, d in G.edges(data=True):
            writer.writerow([u, v, d["weight"]])
    print(f"wrote {OUT_PNG}: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges")
    print(f"wrote {OUT_CSV}")
    print("top persons:", ", ".join(f"{n}({person_count[n]})"
                                    for n in names[:20]))


if __name__ == "__main__":
    main()

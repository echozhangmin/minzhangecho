"""Force-directed (D3.js) interactive network of people around 太祖.

Same graph as network.py, but rendered with a live D3 force simulation that can
be dragged, zoomed and hovered. Written to
output/zhuyuanzhang_network_force.html.

Run from the repository root:  python plot_force.py
"""
import json

from network import build_graph, NAME2GROUP, GROUP_COLOR, TARGET

OUT = "output/zhuyuanzhang_network_force.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>Force-directed network around 太祖 (朱元璋)</title>
<style>
  body {{ margin: 0; font-family: "Songti SC", "PingFang SC", sans-serif; }}
  h2 {{ margin: 10px 16px 0; color: #333; }}
  p.note {{ margin: 4px 16px 8px; color: #777; font-size: 13px; }}
  svg {{ width: 100%; height: 880px; display: block; cursor: grab; }}
  .links line {{ stroke: #999; stroke-opacity: 0.45; }}
  .nodes circle {{ stroke: #fff; stroke-width: 1.5; cursor: pointer; }}
  .labels text {{ font-size: 12px; fill: #222; pointer-events: none;
                  paint-order: stroke; stroke: #fff; stroke-width: 3px; }}
  #tip {{ position: absolute; padding: 6px 10px; background: rgba(0,0,0,.8);
          color: #fff; border-radius: 4px; font-size: 13px; pointer-events: none;
          opacity: 0; transition: opacity .1s; }}
</style>
<script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
<h2>Force-directed network around 太祖 (朱元璋) in the Mingshi</h2>
<p class="note">drag = 拖动节点；滚轮 = 缩放；悬停 = 查看阵营与共现次数。
节点大小 = 与太祖共现次数，连线粗细 = 同句共现次数。</p>
<div id="tip"></div>
<svg></svg>
<script>
const data = {data};
const color = {colors};
const width = 1200, height = 880;

const svg = d3.select("svg").attr("viewBox", [0, 0, width, height]);
const g = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.3, 4]).on("zoom", (e) => g.attr("transform", e.transform)));

const link = g.append("g").attr("class", "links")
  .selectAll("line").data(data.links).join("line")
  .attr("stroke-width", (d) => 0.5 + d.weight * 0.35);

const node = g.append("g").attr("class", "nodes")
  .selectAll("circle").data(data.nodes).join("circle")
  .attr("r", (d) => (d.isTarget ? 26 : 6 + d.freq * 1.3))
  .attr("fill", (d) => (d.isTarget ? "#c0392b" : color[d.group] || "#34495e"));

const label = g.append("g").attr("class", "labels")
  .selectAll("text").data(data.nodes).join("text")
  .attr("text-anchor", "middle").attr("dy", -14).text((d) => d.id);

const tip = d3.select("#tip");
node.on("mousemove", (e, d) => {{
    tip.style("opacity", 1)
       .style("left", (e.pageX + 12) + "px")
       .style("top", (e.pageY + 12) + "px")
       .html(d.isTarget ? "<b>太祖</b> (朱元璋)"
            : "<b>" + d.id + "</b><br>阵营: " + d.group + "<br>与太祖共现: " + d.freq + " 次");
  }}).on("mouseleave", () => tip.style("opacity", 0));

const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id((d) => d.id)
        .distance((d) => 40 + 120 / Math.sqrt(d.weight))
        .strength((d) => Math.min(1, d.weight / 20)))
  .force("charge", d3.forceManyBody().strength(-260))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius((d) => (d.isTarget ? 28 : 8 + d.freq * 1.3) + 4))
  .on("tick", () => {{
    link.attr("x1", (d) => d.source.x).attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x).attr("y2", (d) => d.target.y);
    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
    label.attr("x", (d) => d.x).attr("y", (d) => d.y);
  }});

node.call(d3.drag()
  .on("start", (e, d) => {{ if (!e.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y; }})
  .on("drag", (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
  .on("end", (e, d) => {{ if (!e.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null; }}));
</script>
</body>
</html>
"""


def main():
    G, person_count, names = build_graph()

    nodes = [{"id": TARGET, "group": "太祖", "freq": 0, "isTarget": True}]
    for n in G.nodes:
        if n == TARGET:
            continue
        nodes.append({"id": n, "group": NAME2GROUP.get(n, "其他"),
                      "freq": person_count[n], "isTarget": False})
    links = [{"source": u, "target": v, "weight": d["weight"]}
             for u, v, d in G.edges(data=True)]

    html = TEMPLATE.format(
        data=json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False),
        colors=json.dumps(GROUP_COLOR, ensure_ascii=False))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {OUT}: {len(nodes)} nodes, {len(links)} links")


if __name__ == "__main__":
    main()

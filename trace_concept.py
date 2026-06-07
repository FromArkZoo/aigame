#!/usr/bin/env python3
"""Robust concept-tracer for the aigame knowledge graph.

Works around graphify's fragile substring+IDF `query`/`path`/`explain` matcher,
which anchors on high-IDF *code* symbols and can't disambiguate long
parenthetical concept labels. This resolves a concept by case-insensitive
label substring, then traverses graphify-out/graph.json directly (both
directions), grouping the neighbourhood by run / source file so cross-run
lineage reads cleanly.

Lives at the repo root so it survives `rm -rf graphify-out`. It locates the
graph automatically (graphify-out/graph.json next to this file, or graph.json
beside it as a fallback).

Usage:
    python trace_concept.py "<label substring>"               # neighbourhood of matching concept(s)
    python trace_concept.py "<A substring>" "<B substring>"   # shortest path A->B (undirected)
    python trace_concept.py --depth 2 "<substring>"           # widen traversal depth (default 1)
"""
import json, sys, re
from pathlib import Path
from collections import defaultdict, deque

_here = Path(__file__).resolve().parent
_candidates = (_here / "graphify-out" / "graph.json", _here / "graph.json")
GRAPH = next((c for c in _candidates if c.exists()), _candidates[0])

def load():
    if not GRAPH.exists():
        sys.exit(f"graph not found — looked for {' and '.join(str(c) for c in _candidates)}. "
                 f"Run /graphify on this repo first.")
    d = json.loads(GRAPH.read_text())
    nodes = {n["id"]: n for n in d["nodes"]}
    adj = defaultdict(list)      # undirected, with direction/relation tags
    for e in d["links"]:
        s, t = e["source"], e["target"]
        rel, conf = e.get("relation", "?"), e.get("confidence", "?")
        adj[s].append((t, rel, conf, "->"))
        adj[t].append((s, rel, conf, "<-"))
    return nodes, adj

def find(nodes, sub):
    sub = sub.lower()
    hits = [i for i, n in nodes.items() if sub in (n.get("label", "") or "").lower()]
    # prefer concept/document/rationale nodes over code symbols for concept queries
    hits.sort(key=lambda i: (nodes[i].get("file_type") not in ("concept", "document", "rationale"), len(nodes[i].get("label", ""))))
    return hits

def runtag(n):
    f = (n.get("source_file") or "")
    m = re.search(r"(run\d+|r\d+[_a-z]*|R\d+)", f) or re.search(r"(R\d+)", n.get("label", ""))
    return m.group(1) if m else (f.split("/")[0] if "/" in f else f or "(root)")

def neighbourhood(nodes, adj, seeds, depth):
    seen = set(seeds); frontier = set(seeds); layers = []
    for _ in range(depth):
        nxt = set()
        for u in frontier:
            for (v, rel, conf, d) in adj.get(u, []):
                if v not in seen:
                    nxt.add(v); seen.add(v)
        layers.append(nxt); frontier = nxt
    return layers

def shortest_path(nodes, adj, a, b):
    prev = {a: None}; q = deque([a])
    while q:
        u = q.popleft()
        if u == b: break
        for (v, rel, conf, d) in adj.get(u, []):
            if v not in prev:
                prev[v] = (u, rel, conf, d); q.append(v)
    if b not in prev: return None
    path = []; cur = b
    while cur is not None and prev[cur] is not None:
        u, rel, conf, d = prev[cur]; path.append((u, cur, rel, conf)); cur = u
    return list(reversed(path))

def main():
    args = sys.argv[1:]
    depth = 1
    if "--depth" in args:
        i = args.index("--depth"); depth = int(args[i + 1]); del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    nodes, adj = load()
    if len(args) == 2:
        A, B = find(nodes, args[0]), find(nodes, args[1])
        if not A or not B:
            print("no match for one endpoint"); return
        a, b = A[0], B[0]
        print(f"A = {nodes[a]['label']}\nB = {nodes[b]['label']}\n")
        p = shortest_path(nodes, adj, a, b)
        if not p:
            print("No path — these concepts are NOT connected in the graph (informative: no shared lineage).")
            return
        print(f"Path ({len(p)} hops):")
        for u, v, rel, conf in p:
            print(f"  {nodes[u]['label']}  --{rel}[{conf}]-->  {nodes[v]['label']}")
        return
    sub = args[0]
    seeds = find(nodes, sub)
    if not seeds:
        print(f"no concept node matches '{sub}'"); return
    print(f"{len(seeds)} node(s) match '{sub}'. Anchoring on concept/doc nodes:")
    for i in seeds[:6]:
        print(f"  • {nodes[i]['label']}  [{nodes[i].get('source_file','')}]")
    layers = neighbourhood(nodes, adj, set(seeds), depth)
    for d, layer in enumerate(layers, 1):
        byrun = defaultdict(list)
        for i in layer:
            byrun[runtag(nodes[i])].append(nodes[i]["label"])
        print(f"\n-- depth {d}: {len(layer)} neighbours across {len(byrun)} run/areas --")
        for r in sorted(byrun):
            items = byrun[r][:6]; more = "" if len(byrun[r]) <= 6 else f" (+{len(byrun[r])-6})"
            print(f"  [{r}] {', '.join(items)}{more}")

if __name__ == "__main__":
    main()

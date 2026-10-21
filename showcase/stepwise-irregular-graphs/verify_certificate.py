"""Check the finite counterexample certificate using only Python's standard library.

This checks arithmetic and an explicit ordinary graph. The universal SI
non-realizability argument is the counting proof accompanying this file.
It does not set any MathLottery review or verification status.
"""

import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

CERTIFICATE = {
    "multiplicities": {"1": 1, "2": 3, "3": 1, "4": 1, "5": 6, "6": 4},
    "left": ["a1", "a2", "a3", "a4", "b", "c1", "c2", "c3"],
    "right": ["u1", "u2", "u3", "u4", "u5", "u6", "v", "w"],
    "neighbors": {
        "a1": ["u1", "u2", "u3", "u4", "u5", "u6"],
        "a2": ["u1", "u2", "u3", "u4", "u5", "u6"],
        "a3": ["u1", "u2", "u3", "u4", "u5", "u6"],
        "a4": ["u1", "u2", "u3", "u4", "u5", "v"],
        "b": ["u1", "u2", "u6", "v"],
        "c1": ["u3", "u4"],
        "c2": ["u5", "u6"],
        "c3": ["v", "w"],
    },
    "obstruction_degree_class": 2,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(certificate):
    n = {int(k): v for k, v in certificate["multiplicities"].items()}
    require(n and all(type(v) is int and v > 0 for v in n.values()),
            "Multiplicities must be positive integers")
    m, maximum = min(n), max(n)
    require(1 <= m < maximum, "Positive, distinct minimum and maximum")
    require(set(n) == set(range(m, maximum + 1)), "Missing degree class")
    require(n[maximum - 1] >= max(maximum, n[maximum]), "Top-layer bound")
    even = sum(i * count for i, count in n.items() if i % 2 == 0)
    odd = sum(i * count for i, count in n.items() if i % 2 == 1)
    require(even == odd, "Parity balance")

    # Additional natural conditions, not added to the original conjecture.
    require(n.get(1, 0) <= n.get(2, 0), "Leaf bound")
    require(maximum * n[maximum] < (maximum - 1) * n[maximum - 1],
            "Strict top-end incidence capacity")
    require(all(i <= n.get(i - 1, 0) + n.get(i + 1, 0) for i in n),
            "Individual vertex neighbor capacity")

    left_list, right_list = certificate["left"], certificate["right"]
    left, right = set(left_list), set(right_list)
    require(len(left) == len(left_list) and len(right) == len(right_list),
            "Repeated vertex label")
    require(not left & right, "Bipartition sides must be disjoint")
    neighbors = certificate["neighbors"]
    require(set(neighbors) == left, "One neighborhood per left vertex")
    adjacency = {vertex: set() for vertex in left | right}
    edge_count = 0
    for u, targets in neighbors.items():
        require(len(targets) == len(set(targets)), "Repeated edge")
        require(set(targets) <= right, "Edge must cross the bipartition")
        for v in targets:
            adjacency[u].add(v)
            adjacency[v].add(u)
            edge_count += 1
    degrees = {v: len(targets) for v, targets in adjacency.items()}
    require(Counter(degrees.values()) == Counter(n), "Degree multiset")
    require(edge_count == even, "Edge count")
    start = left_list[0]
    reached, stack = {start}, [start]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex] - reached:
            reached.add(neighbor)
            stack.append(neighbor)
    require(reached == left | right, "Graph must be connected")
    require(all(degrees[u] % 2 == 0 for u in left), "Even-degree left side")
    require(all(degrees[v] % 2 == 1 for v in right), "Odd-degree right side")

    # Every SI graph obeys k*n_k <= (k-1)*n_(k-1)+(k+1)*n_(k+1).
    k = certificate["obstruction_degree_class"]
    require(k in n, "Obstruction class must exist")
    required = k * n[k]
    available = (k - 1) * n.get(k - 1, 0) + (k + 1) * n.get(k + 1, 0)
    require(required > available, "Strict SI capacity obstruction required")
    return {
        "vertices": len(adjacency),
        "edges": edge_count,
        "even_degree_sum": even,
        "odd_degree_sum": odd,
        "degree_multiplicities": dict(sorted(n.items())),
        "ordinary_graph_simple_connected_bipartite": True,
        "si_required_incident_edges": required,
        "si_available_neighbor_degree": available,
        "independent_review_status": "not performed by this checker",
    }


if __name__ == "__main__":
    data = deepcopy(CERTIFICATE)
    if len(sys.argv) > 1:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(verify(data), ensure_ascii=False, indent=2))

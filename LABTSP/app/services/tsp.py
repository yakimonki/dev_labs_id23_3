from app.schemas.graph import Graph, PathResult
import networkx as nx


def solve_tsp(graph: Graph) -> PathResult:
    G = nx.Graph()

    G.add_nodes_from(graph.nodes)

    for edge in graph.edges:
        G.add_edge(edge[0], edge[1], weight=1)

    try:
        path = list(nx.dfs_preorder_nodes(G, source=graph.nodes[0]))
        path.append(path[0])
        return PathResult(path=path, total_distance=float(len(path) - 1))
    except nx.NetworkXError:
        return PathResult(path=[], total_distance=0.0)

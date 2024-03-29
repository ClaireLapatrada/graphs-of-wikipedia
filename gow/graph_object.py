from __future__ import annotations
from visualize_template import *
from gow.bfs import *
from collections import defaultdict
from typing import Any

class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    item: Any
    neighbours: set[_Vertex]

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours

class Graph:
    """A graph.

    Representation Invariants:
        - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.
        """
        self._vertices[item] = _Vertex(item, set())

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            self.add_vertex(item1)
            # We didn't find an existing vertex for both items.
            raise ValueError


    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            it1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in it1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError



    def add_all_edges(self, edges: set[tuple[Any, Any]]) -> None:
        """Add all given edges to this graph.

        Each element of edges is a tuple (x, y), representing the edge {x, y}.
        If an object in a given edge isn't represented by a vertex in this graph,
        add a new vertex containing the object to this graph before adding the edge.
        We strongly encourage you to make use of the Graph methods defined above.

        This method should NOT raise any ValueErrors.

        Preconditions:
        - all(edge[0] != edge[1] for edge in edges)

        >>> example_graph = Graph()
        >>> example_edges = {(1, 2), (1, 3), (3, 4)}
        >>> example_graph.add_all_edges(example_edges)
        >>> example_graph.get_neighbours(1) == {2, 3}
        True
        >>> example_graph.get_neighbours(3) == {1, 4}
        True
        """
        for v0, v1 in edges:
            if v0 not in self._vertices:
                self.add_vertex(v0)
            if v1 not in self._vertices:
                self.add_vertex(v1)
            self.add_edge(v0, v1)

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'user', 'book'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def all_edge(self) -> set:
        """
        >>> example_graph = Graph()
        >>> example_graph.add_vertex(10)
        >>> example_graph.add_vertex(20)
        >>> example_graph.add_vertex(30)
        >>> example_graph.add_vertex(40)
        >>> example_graph.add_edge(10, 20)
        >>> example_graph.add_edge(20, 30)
        >>> example_graph.add_edge(30, 40)
        >>> example_graph.all_edge()
        """
        edge_set = set()
        visited = set()
        for u in self._vertices:
            for i in self._vertices[u].neighbours:
                if i.item not in visited:
                    edge_set.add((u, i.item))
                    visited.add(u)
        return edge_set

    def create_subgraph_from_paths(graph, paths):
        """Create a new Graph containing only the nodes and edges from the given paths."""
        dict_graph = defaultdict(list)
        for path in paths:
            for i in range(len(path) - 1):
                dict_graph[path[i]].append(path[i + 1])

        graph = Graph()
        for page in dict_graph:
            graph.add_vertex(page)

        for page in dict_graph:
            for i in range(len(dict_graph[page])):
                if not dict_graph[page][i] in graph._vertices:
                    graph.add_vertex(dict_graph[page][i])
                graph.add_edge(page, dict_graph[page][i])

        return graph

def load_gow(pages_file: str) -> Graph:
    graph = Graph()
    unique_pages = {}

    # Step 1: Add all vertices
    with open(pages_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            page_id, page_title = row['page_id'], row['page_title']
            unique_pages[page_id] = page_title
            graph.add_vertex(page_title)

    with open(pages_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            page_id = row['page_id']
            page_title = unique_pages[page_id]
            outgoing_links = ast.literal_eval(row['outgoing_links'])

            for other_id in outgoing_links:
                other_title = unique_pages.get(str(other_id))
                if other_title:  # Check if the other page is in the dataset
                    graph.add_edge(page_title, other_title)

    return graph


def load_dict_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    else:
        return {}

def load_gow_json(pages_file: str):
    graph = Graph()
    unique_pages = load_dict_from_file(pages_file)

    #add_vertex
    for page in unique_pages:
        graph.add_vertex(page)

    #add_edge
    for page in unique_pages:
        for i in range(len(unique_pages[page])):
            if not unique_pages[page][i] in graph._vertices:
                graph.add_vertex(unique_pages[page][i])
            graph.add_edge(page, unique_pages[page][i])

    return graph, unique_pages


#External Methods
def generate_complete_graph(n: int) -> Graph:
    """Return a graph of n vertices where all pairs of vertices are adjacent.

    The vertex items are the numbers 0 through n - 1, inclusive.
    When n == 0, return an empty Graph.

    Preconditions:
        - n >= 0
    """

    graph_so_far = Graph()

    for i in range(n):
        graph_so_far.add_vertex(i)

        # Add edges to all previous vertices (0 <= j < i)
        for j in range(0, i):
            graph_so_far.add_edge(i, j)

    return graph_so_far


if __name__ == '__main__':
    # graph = load_gow('../database/pages_links.csv')
    # visualize_paths(graph, 'Animals' , 'Dog')
    graph, graph_dict = load_gow_json('../database/mini_graph.json')
    visualize_paths(graph, graph_dict, 'Toronto Metropolitan University', 'Rhombicosidodecahedron')
    #claire

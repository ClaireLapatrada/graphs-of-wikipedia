from graph_object import *
from plotly.graph_objs import Scatter, Figure
from gow.bfs import *
import networkx as nx

def edge_in_path(edge, path):
    """Check if an edge is in the shortest path."""
    return any(edge == (path[i], path[i + 1]) or edge == (path[i + 1], path[i]) for i in range(len(path) - 1))


def convert_to_networkx(custom_graph):
    """Convert a custom graph object to a NetworkX graph."""
    nx_graph = nx.Graph()
    # Assuming your custom Graph has methods to access its vertices and edges
    for vertex in custom_graph._vertices:
        nx_graph.add_node(vertex)
    for edge in custom_graph.all_edge():
        # Assuming get_edges() returns a list of tuples (source, target)
        nx_graph.add_edge(edge[0], edge[1])
    return nx_graph

def visualize_paths(graph, graph_dict, page_id1, page_id2):
    """
    Visualize all paths between two vertices in a graph using networkx and plotly.

    Args:
    - graph: The graph object (as a networkx Graph).
    - page_id1, page_id2: The IDs of the two vertices to find paths between.
    """
    all_paths = BFS_paths(graph_dict, page_id1, page_id2)
    shortest_path = BFS_path(graph_dict, page_id1, page_id2)
    print(all_paths)

    subgraph = graph.create_subgraph_from_paths(all_paths)
    print(subgraph._vertices)


    path_lengths = bfs_shortest_path_lengths(graph, page_id1)



    nx_subgraph = convert_to_networkx(subgraph)
    pos = nx.spring_layout(nx_subgraph)


    x_values, y_values = zip(*pos.values())
    min_x, max_x = min(x_values), max(x_values)
    #
    # Set the start and end nodes at the extreme sides of the layout
    pos[page_id1] = (min_x - 0.1 * (max_x - min_x), 0)  # Slightly left from the minimum x value
    pos[page_id2] = (max_x + 0.1 * (max_x - min_x), 0)  # Slightly right from the maximum x value

    # Prepare a base color scale and special color for the destination
    base_colors = ['#ff0000', '#ff7f00', '#ffff00', '#7fff00', '#00ff00', '#0000ff']
    destination_color = '#000000'  # Special color for the destination

    max_distance = max(path_lengths.values(), default=0)
    color_step = max(1, (len(base_colors) - 1) / (max_distance or 1))

    # Create a color mapping for each node
    node_color_mapping = {}
    for node, distance in path_lengths.items():
        if node == page_id2:  # Apply special color to the destination node
            node_color_mapping[node] = destination_color
        else:
            color_index = int(distance * color_step) % len(base_colors)
            node_color_mapping[node] = base_colors[color_index]

    # Nodes
    node_x = []
    node_y = []
    text = []
    node_colors = []  # List to hold colors for each node

    for node in nx_subgraph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(str(node))
        # Fetch color from mapping, default to a fallback color if not found
        node_colors.append(node_color_mapping.get(node, "#000000"))  # Default/fallback color

    # Now, create the node_trace with the correct colors for each node
    node_trace = Scatter(
        x=node_x, y=node_y, text=text, mode='markers+text', hoverinfo='text',
        marker=dict(
            color=node_colors,  # Apply the color list here
            size=10,
            line=dict(width=2)
        )
    )

    # Separate lists for shortest path edges and other edges
    shortest_edge_x, shortest_edge_y = [], []
    other_edge_x, other_edge_y = [], []

    for edge in nx_subgraph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        if edge_in_path(edge, shortest_path):
            shortest_edge_x.extend([x0, x1, None])
            shortest_edge_y.extend([y0, y1, None])
        else:
            other_edge_x.extend([x0, x1, None])
            other_edge_y.extend([y0, y1, None])


    shortest_path_trace = Scatter(
        x=shortest_edge_x, y=shortest_edge_y,
        line=dict(width=2.5, color='black'),  # Make these edges thicker and gold
        hoverinfo='text',
        text='Shortest Path',  # Hover text
        mode='lines'
    )

    other_edges_trace = Scatter(
        x=other_edge_x, y=other_edge_y,
        line=dict(width=0.5, color='#888'),  # Regular edges
        hoverinfo='none',
        mode='lines'
    )

    fig = Figure(data=[other_edges_trace, shortest_path_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig.show()

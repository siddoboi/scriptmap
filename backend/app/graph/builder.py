import networkx as nx
from app.models.script_data import ScriptData


def build_graph(script_data: ScriptData) -> nx.Graph:
    """
    Build a weighted undirected graph from a ScriptData object.

    Nodes: one per unique speaking character
        - line_count: total dialogue lines
        - act_counts: dialogue lines split by act {1: N, 2: N, 3: N}

    Edges: one per character pair that share at least one scene
        - weight: number of scenes they share
    """
    graph = nx.Graph()

    # Build node attributes
    char_act_counts: dict[str, dict[int, int]] = {}

    for character in script_data.characters:
        char_act_counts[character] = {1: 0, 2: 0, 3: 0}

    for scene in script_data.scenes:
        act = scene.act if scene.act in (1, 2, 3) else 1
        for line in scene.dialogue:
            if line.character in char_act_counts:
                char_act_counts[line.character][act] += 1

    # Add nodes
    for i, (character, line_count) in enumerate(
        sorted(script_data.characters.items(),
               key=lambda x: x[1], reverse=True)
    ):
        graph.add_node(
            character,
            label=character,
            line_count=line_count,
            act_counts=char_act_counts[character],
            color_index=i % 10,  # D3 schemeTableau10 has 10 colors
        )

    # Build edges from scene co-occurrence
    for scene in script_data.scenes:
        characters = scene.characters_present
        if len(characters) < 2:
            continue

        # Add edge between every pair of characters in this scene
        for i in range(len(characters)):
            for j in range(i + 1, len(characters)):
                a, b = characters[i], characters[j]
                if graph.has_node(a) and graph.has_node(b):
                    if graph.has_edge(a, b):
                        graph[a][b]['weight'] += 1
                    else:
                        graph.add_edge(a, b, weight=1)

    return graph
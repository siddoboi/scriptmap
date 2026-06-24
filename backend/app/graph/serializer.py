import networkx as nx
from app.models.script_data import ScriptData


def to_json(
    graph: nx.Graph,
    script_data: ScriptData,
    sentiment_arcs: dict,
) -> dict:
    """
    Serialize a NetworkX graph + ScriptData + sentiment arcs
    into the JSON shape expected by the frontend GraphResponse schema.
    """
    nodes = []
    for node_id, attrs in graph.nodes(data=True):
        act_counts = attrs.get('act_counts', {1: 0, 2: 0, 3: 0})
        nodes.append({
            'id':          node_id,
            'label':       attrs.get('label', node_id),
            'line_count':  attrs.get('line_count', 0),
            'act_counts':  {
                'act_1': act_counts.get(1, 0),
                'act_2': act_counts.get(2, 0),
                'act_3': act_counts.get(3, 0),
            },
            'color_index': attrs.get('color_index', 0),
        })

    # Sort nodes by line_count descending for consistent frontend rendering
    nodes.sort(key=lambda n: n['line_count'], reverse=True)

    edges = []
    for source, target, attrs in graph.edges(data=True):
        edges.append({
            'source': source,
            'target': target,
            'weight': attrs.get('weight', 1),
        })

    # Sort edges by weight descending
    edges.sort(key=lambda e: e['weight'], reverse=True)

    metadata = {
        'title':            script_data.title,
        'total_pages':      script_data.total_pages,
        'total_characters': len(script_data.characters),
        'total_scenes':     len(script_data.scenes),
        'source_format':    script_data.source_format,
    }

    return {
        'nodes':          nodes,
        'edges':          edges,
        'sentiment_arcs': sentiment_arcs,
        'act_breaks':     script_data.act_breaks,
        'metadata':       metadata,
    }
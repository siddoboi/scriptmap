import pytest
import networkx as nx
from app.graph.builder import build_graph
from app.graph.serializer import to_json
from app.models.script_data import ScriptData, SceneBlock, DialogueLine, LineType


def make_simple_script() -> ScriptData:
    """Build a minimal ScriptData for unit testing without parsing a file."""
    line_a1 = DialogueLine(
        character="ALICE", text="Hello.", page=1,
        line_type=LineType.DIALOGUE, scene_id=1
    )
    line_b1 = DialogueLine(
        character="BOB", text="Hi there.", page=1,
        line_type=LineType.DIALOGUE, scene_id=1
    )
    line_a2 = DialogueLine(
        character="ALICE", text="Goodbye.", page=5,
        line_type=LineType.DIALOGUE, scene_id=2
    )
    line_c2 = DialogueLine(
        character="CAROL", text="See you.", page=5,
        line_type=LineType.DIALOGUE, scene_id=2
    )

    scene1 = SceneBlock(
        scene_id=1, heading="INT. ROOM - DAY", act=1,
        page_start=1, page_end=3,
        characters_present=["ALICE", "BOB"],
        dialogue=[line_a1, line_b1],
    )
    scene2 = SceneBlock(
        scene_id=2, heading="EXT. STREET - NIGHT", act=2,
        page_start=5, page_end=7,
        characters_present=["ALICE", "CAROL"],
        dialogue=[line_a2, line_c2],
    )

    return ScriptData(
        title="Test Script",
        total_pages=10,
        scenes=[scene1, scene2],
        characters={"ALICE": 2, "BOB": 1, "CAROL": 1},
        act_breaks=[3, 8],
        source_format="pdf",
    )


# ── build_graph ───────────────────────────────────────────────────────────────

def test_build_graph_returns_nx_graph():
    script = make_simple_script()
    graph = build_graph(script)
    assert isinstance(graph, nx.Graph)

def test_build_graph_correct_node_count():
    script = make_simple_script()
    graph = build_graph(script)
    assert graph.number_of_nodes() == 3  # ALICE, BOB, CAROL

def test_build_graph_correct_edge_count():
    script = make_simple_script()
    graph = build_graph(script)
    # ALICE-BOB (scene 1), ALICE-CAROL (scene 2)
    assert graph.number_of_edges() == 2

def test_build_graph_node_has_line_count():
    script = make_simple_script()
    graph = build_graph(script)
    assert graph.nodes["ALICE"]["line_count"] == 2
    assert graph.nodes["BOB"]["line_count"] == 1

def test_build_graph_node_has_color_index():
    script = make_simple_script()
    graph = build_graph(script)
    for node in graph.nodes:
        assert "color_index" in graph.nodes[node]
        assert 0 <= graph.nodes[node]["color_index"] <= 9

def test_build_graph_edge_weight_correct():
    script = make_simple_script()
    graph = build_graph(script)
    assert graph["ALICE"]["BOB"]["weight"] == 1
    assert graph["ALICE"]["CAROL"]["weight"] == 1

def test_build_graph_no_self_edges():
    script = make_simple_script()
    graph = build_graph(script)
    for u, v in graph.edges():
        assert u != v

def test_build_graph_isolated_character_no_edge():
    script = make_simple_script()
    # Add a character who only appears alone
    script.characters["SOLO"] = 5
    lone_line = DialogueLine(
        character="SOLO", text="Alone.", page=9,
        line_type=LineType.DIALOGUE, scene_id=3
    )
    lone_scene = SceneBlock(
        scene_id=3, heading="INT. CAVE - DAY", act=3,
        page_start=9, page_end=10,
        characters_present=["SOLO"],
        dialogue=[lone_line],
    )
    script.scenes.append(lone_scene)
    graph = build_graph(script)
    assert graph.has_node("SOLO")
    assert graph.degree["SOLO"] == 0

def test_build_graph_accumulates_edge_weight():
    script = make_simple_script()
    # Add a second scene with same pair ALICE-BOB
    extra_line_a = DialogueLine(
        character="ALICE", text="Again.", page=8,
        line_type=LineType.DIALOGUE, scene_id=3
    )
    extra_line_b = DialogueLine(
        character="BOB", text="Indeed.", page=8,
        line_type=LineType.DIALOGUE, scene_id=3
    )
    extra_scene = SceneBlock(
        scene_id=3, heading="INT. ROOM - LATER", act=3,
        page_start=8, page_end=9,
        characters_present=["ALICE", "BOB"],
        dialogue=[extra_line_a, extra_line_b],
    )
    script.scenes.append(extra_scene)
    graph = build_graph(script)
    assert graph["ALICE"]["BOB"]["weight"] == 2


# ── to_json / serializer ──────────────────────────────────────────────────────

def test_serializer_returns_dict():
    script = make_simple_script()
    graph = build_graph(script)
    result = to_json(graph, script, {})
    assert isinstance(result, dict)

def test_serializer_has_required_keys():
    script = make_simple_script()
    graph = build_graph(script)
    result = to_json(graph, script, {})
    assert "nodes" in result
    assert "edges" in result
    assert "sentiment_arcs" in result
    assert "act_breaks" in result
    assert "metadata" in result

def test_serializer_node_structure():
    script = make_simple_script()
    graph = build_graph(script)
    result = to_json(graph, script, {})
    for node in result["nodes"]:
        assert "id" in node
        assert "label" in node
        assert "line_count" in node
        assert "act_counts" in node
        assert "color_index" in node

def test_serializer_act_counts_structure():
    script = make_simple_script()
    graph = build_graph(script)
    result = to_json(graph, script, {})
    for node in result["nodes"]:
        ac = node["act_counts"]
        assert "act_1" in ac
        assert "act_2" in ac
        assert "act_3" in ac

def test_serializer_edge_structure():
    script = make_simple_script()
    graph = build_graph(script)
    result = to_json(graph, script, {})
    for edge in result["edges"]:
        assert "source" in edge
        assert "target" in edge
        assert "weight" in edge

def test_serializer_nodes_sorted_by_line_count():
    script = make_simple_script()
    graph = build_graph(script)
    result = to_json(graph, script, {})
    counts = [n["line_count"] for n in result["nodes"]]
    assert counts == sorted(counts, reverse=True)

def test_serializer_metadata_correct():
    script = make_simple_script()
    graph = build_graph(script)
    result = to_json(graph, script, {})
    assert result["metadata"]["title"] == "Test Script"
    assert result["metadata"]["total_pages"] == 10
    assert result["metadata"]["source_format"] == "pdf"


# ── Integration with real fixture ─────────────────────────────────────────────

def test_graph_pulp_fiction_node_count():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    graph = build_graph(result)
    assert graph.number_of_nodes() == len(result.characters)

def test_graph_pulp_fiction_jules_vincent_edge():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    graph = build_graph(result)
    assert graph.has_edge("JULES", "VINCENT")
    assert graph["JULES"]["VINCENT"]["weight"] >= 10
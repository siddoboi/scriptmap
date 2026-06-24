from app.parser.pdf_parser import parse
from app.nlp.act_detector import assign_acts
from app.nlp.sentiment import score_script
from app.graph.builder import build_graph
from app.graph.serializer import to_json

result = parse("tests/fixtures/pulp_fiction.pdf")
result = assign_acts(result)
arcs = score_script(result)
graph = build_graph(result)
payload = to_json(graph, result, arcs)

print(f"Nodes: {len(payload['nodes'])}")
print(f"Edges: {len(payload['edges'])}")
print(f"Act breaks: {payload['act_breaks']}")
print(f"Metadata: {payload['metadata']}")
print()
print("Top 5 nodes:")
for node in payload['nodes'][:5]:
    print(f"  {node['id']:20s}  lines={node['line_count']:4d}  color={node['color_index']}")
print()
print("Top 5 edges by weight:")
for edge in payload['edges'][:5]:
    print(f"  {edge['source']:15s} <-> {edge['target']:15s}  weight={edge['weight']}")
from app.parser.pdf_parser import parse
from app.nlp.act_detector import assign_acts
from app.nlp.sentiment import score_script

result = parse("tests/fixtures/pulp_fiction.pdf")
result = assign_acts(result)
arcs = score_script(result)

print(f"Characters with arcs: {len(arcs)}")
print()
print("JULES first 5 sentiment points:")
for point in arcs["JULES"][:5]:
    print(f"  page={point['page']}  raw={point['raw']:+.3f}  score={point['score']:+.3f}")

print()
print("VINCENT sentiment range:")
scores = [p["score"] for p in arcs["VINCENT"]]
print(f"  min={min(scores):+.3f}  max={max(scores):+.3f}  avg={sum(scores)/len(scores):+.3f}")
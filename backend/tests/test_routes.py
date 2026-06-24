import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

PULP_FICTION = "tests/fixtures/pulp_fiction.pdf"
PARASITE     = "tests/fixtures/parasite.pdf"
SCANNED      = "tests/fixtures/west_wing_pilot.pdf"


# ── Health ────────────────────────────────────────────────────────────────────

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── Upload ────────────────────────────────────────────────────────────────────

def test_upload_valid_pdf():
    with open(PULP_FICTION, "rb") as f:
        response = client.post("/upload", files={"file": ("pulp_fiction.pdf", f, "application/pdf")})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "parsed"
    assert len(data["character_list"]) > 0
    assert data["total_characters"] > 0
    assert data["total_scenes"] > 0
    assert data["total_pages"] > 0

def test_upload_returns_correct_characters():
    with open(PULP_FICTION, "rb") as f:
        response = client.post("/upload", files={"file": ("pulp_fiction.pdf", f, "application/pdf")})
    data = response.json()
    assert "JULES" in data["character_list"]
    assert "VINCENT" in data["character_list"]

def test_upload_scanned_pdf_returns_422():
    with open(SCANNED, "rb") as f:
        response = client.post("/upload", files={"file": ("west_wing.pdf", f, "application/pdf")})
    assert response.status_code == 422
    assert response.json()["detail"]["error_code"] == "SCANNED_PDF"

def test_upload_unsupported_format_returns_415():
    response = client.post(
        "/upload",
        files={"file": ("script.txt", b"some text content", "text/plain")}
    )
    assert response.status_code == 415
    assert response.json()["detail"]["error_code"] == "UNSUPPORTED_FORMAT"

def test_upload_fdx():
    with open("tests/fixtures/parasite.fdx", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("parasite.fdx", f, "application/octet-stream")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "parsed"
    assert "KI-WOO" in data["character_list"]


# ── Graph ─────────────────────────────────────────────────────────────────────

def _get_session_id() -> str:
    with open(PULP_FICTION, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("pulp_fiction.pdf", f, "application/pdf")}
        )
    return response.json()["session_id"]

def test_get_graph_valid_session():
    session_id = _get_session_id()
    response = client.get(f"/graph/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "sentiment_arcs" in data
    assert "act_breaks" in data
    assert "metadata" in data

def test_get_graph_nodes_structure():
    session_id = _get_session_id()
    response = client.get(f"/graph/{session_id}")
    nodes = response.json()["nodes"]
    assert len(nodes) > 0
    for node in nodes[:3]:
        assert "id" in node
        assert "line_count" in node
        assert "act_counts" in node
        assert "color_index" in node

def test_get_graph_edges_structure():
    session_id = _get_session_id()
    response = client.get(f"/graph/{session_id}")
    edges = response.json()["edges"]
    assert len(edges) > 0
    for edge in edges[:3]:
        assert "source" in edge
        assert "target" in edge
        assert "weight" in edge

def test_get_graph_invalid_session_returns_404():
    response = client.get("/graph/nonexistent-session-id")
    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "SESSION_NOT_FOUND"

def test_get_graph_sentiment_arcs_present():
    session_id = _get_session_id()
    response = client.get(f"/graph/{session_id}")
    arcs = response.json()["sentiment_arcs"]
    assert "JULES" in arcs
    assert len(arcs["JULES"]) > 0


# ── Merge ─────────────────────────────────────────────────────────────────────

def test_merge_valid():
    with open(PULP_FICTION, "rb") as f:
        upload = client.post(
            "/upload",
            files={"file": ("pulp_fiction.pdf", f, "application/pdf")}
        )
    session_id = upload.json()["session_id"]

    response = client.post("/merge", json={
        "session_id": session_id,
        "merges": []  # empty merge - just rebuild graph
    })
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data

def test_merge_invalid_character_returns_422():
    with open(PULP_FICTION, "rb") as f:
        upload = client.post(
            "/upload",
            files={"file": ("pulp_fiction.pdf", f, "application/pdf")}
        )
    session_id = upload.json()["session_id"]

    response = client.post("/merge", json={
        "session_id": session_id,
        "merges": [{"source": "NONEXISTENT", "target": "JULES"}]
    })
    assert response.status_code == 422

def test_merge_invalid_session_returns_404():
    response = client.post("/merge", json={
        "session_id": "fake-session",
        "merges": []
    })
    assert response.status_code == 404
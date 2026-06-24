from pydantic import BaseModel


# ── Graph node and edge ───────────────────────────────────────────────────────

class ActCounts(BaseModel):
    act_1: int
    act_2: int
    act_3: int


class GraphNode(BaseModel):
    id:          str
    label:       str
    line_count:  int
    act_counts:  ActCounts
    color_index: int


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: int


class SentimentPoint(BaseModel):
    page:  int
    score: float
    raw:   float


# ── Metadata ──────────────────────────────────────────────────────────────────

class GraphMetadata(BaseModel):
    title:            str
    total_pages:      int
    total_characters: int
    total_scenes:     int
    source_format:    str


# ── Upload ────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    session_id:       str
    status:           str
    character_list:   list[str]
    total_characters: int
    total_scenes:     int
    total_pages:      int
    parse_warnings:   list[str] = []


# ── Graph ─────────────────────────────────────────────────────────────────────

class GraphResponse(BaseModel):
    nodes:          list[GraphNode]
    edges:          list[GraphEdge]
    sentiment_arcs: dict[str, list[SentimentPoint]]
    act_breaks:     list[int]
    metadata:       GraphMetadata


# ── Merge ─────────────────────────────────────────────────────────────────────

class AliasMerge(BaseModel):
    source: str
    target: str


class MergeRequest(BaseModel):
    session_id: str
    merges:     list[AliasMerge]


class MergeResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ── Compare ───────────────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    error_code: str
    message:    str


class CompareUploadResponse(BaseModel):
    session_a:       str | None
    session_b:       str | None
    status_a:        str
    status_b:        str
    character_list_a: list[str] = []
    character_list_b: list[str] = []
    error_a:         ErrorDetail | None = None
    error_b:         ErrorDetail | None = None
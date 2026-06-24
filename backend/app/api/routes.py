import uuid
import asyncio
from datetime import datetime, timedelta, UTC
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.api.schemas import (
    UploadResponse, GraphResponse, GraphNode, GraphEdge,
    GraphMetadata, SentimentPoint, ActCounts,
    MergeRequest, MergeResponse,
    CompareUploadResponse, ErrorDetail,
)
from app.config import settings
from app.models.script_data import ScriptData
from app.utils.file_utils import (
    validate_upload, write_tmp, delete_tmp, detect_format,
    FileTooLargeError, UnsupportedFormatError,
)
from app.utils.text_layer import ScannedPDFError
from app.parser.pdf_parser import parse as pdf_parse
from app.parser.fdx_parser import parse as fdx_parse
from app.nlp.act_detector import assign_acts
from app.nlp.sentiment import score_script
from app.graph.builder import build_graph
from app.graph.serializer import to_json

router = APIRouter()

# ── In-memory session store ───────────────────────────────────────────────────
_sessions: dict[str, dict] = {}


def _evict_stale_sessions() -> None:
    cutoff = datetime.now(UTC) - timedelta(minutes=settings.session_ttl_minutes)
    stale = [k for k, v in _sessions.items() if v["created_at"] < cutoff]
    for k in stale:
        del _sessions[k]


def _get_session(session_id: str) -> ScriptData:
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail={
            "error_code": "SESSION_NOT_FOUND",
            "message": "Session not found or expired. Please re-upload the screenplay.",
        })
    return _sessions[session_id]["script_data"]


async def _parse_file(file: UploadFile) -> tuple[ScriptData, str]:
    tmp_path = None
    try:
        validate_upload(file)
        tmp_path = await write_tmp(file)
        fmt = detect_format(file.filename or "")

        if fmt == "fdx":
            script_data = await run_in_threadpool(fdx_parse, str(tmp_path))
        else:
            script_data = await run_in_threadpool(pdf_parse, str(tmp_path))

        script_data = await run_in_threadpool(assign_acts, script_data)

        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            "script_data": script_data,
            "created_at": datetime.now(UTC),
        }
        return script_data, session_id

    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail={
            "error_code": "FILE_TOO_LARGE",
            "message": str(e),
        })
    except UnsupportedFormatError as e:
        raise HTTPException(status_code=415, detail={
            "error_code": "UNSUPPORTED_FORMAT",
            "message": str(e),
        })
    except ScannedPDFError as e:
        raise HTTPException(status_code=422, detail={
            "error_code": "SCANNED_PDF",
            "message": str(e),
        })
    except ValueError as e:
        raise HTTPException(status_code=422, detail={
            "error_code": "PARSE_ERROR",
            "message": str(e),
        })
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred during parsing.",
        })
    finally:
        if tmp_path:
            delete_tmp(Path(tmp_path))


def _build_graph_response(script_data: ScriptData) -> dict:
    arcs = score_script(script_data)
    graph = build_graph(script_data)
    return to_json(graph, script_data, arcs)


def _payload_to_graph_response(payload: dict) -> GraphResponse:
    return GraphResponse(
        nodes=[GraphNode(
            id=n["id"], label=n["label"],
            line_count=n["line_count"],
            act_counts=ActCounts(
                act_1=n["act_counts"]["act_1"],
                act_2=n["act_counts"]["act_2"],
                act_3=n["act_counts"]["act_3"],
            ),
            color_index=n["color_index"],
        ) for n in payload["nodes"]],
        edges=[GraphEdge(
            source=e["source"],
            target=e["target"],
            weight=e["weight"],
        ) for e in payload["edges"]],
        sentiment_arcs={
            char: [SentimentPoint(**p) for p in points]
            for char, points in payload["sentiment_arcs"].items()
        },
        act_breaks=payload["act_breaks"],
        metadata=GraphMetadata(**payload["metadata"]),
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    _evict_stale_sessions()
    script_data, session_id = await _parse_file(file)

    char_list = sorted(
        script_data.characters.keys(),
        key=lambda c: script_data.characters[c],
        reverse=True,
    )

    return UploadResponse(
        session_id=session_id,
        status="parsed",
        character_list=char_list,
        total_characters=len(char_list),
        total_scenes=len(script_data.scenes),
        total_pages=script_data.total_pages,
        parse_warnings=script_data.parse_warnings,
    )


@router.get("/graph/{session_id}", response_model=GraphResponse)
async def get_graph(session_id: str):
    script_data = _get_session(session_id)
    payload = await run_in_threadpool(_build_graph_response, script_data)
    return _payload_to_graph_response(payload)


@router.post("/merge", response_model=MergeResponse)
async def merge(request: MergeRequest):
    script_data = _get_session(request.session_id)

    for merge_item in request.merges:
        source = merge_item.source
        target = merge_item.target

        if source not in script_data.characters:
            raise HTTPException(status_code=422, detail={
                "error_code": "MERGE_INVALID",
                "message": f"Character '{source}' not found in session.",
            })
        if target not in script_data.characters:
            raise HTTPException(status_code=422, detail={
                "error_code": "MERGE_INVALID",
                "message": f"Character '{target}' not found in session.",
            })

        script_data.characters[target] += script_data.characters.pop(source)

        for scene in script_data.scenes:
            for line in scene.dialogue:
                if line.character == source:
                    line.character = target
            if source in scene.characters_present:
                scene.characters_present.remove(source)
                if target not in scene.characters_present:
                    scene.characters_present.append(target)

    payload = await run_in_threadpool(_build_graph_response, script_data)

    return MergeResponse(
        nodes=[GraphNode(
            id=n["id"], label=n["label"],
            line_count=n["line_count"],
            act_counts=ActCounts(
                act_1=n["act_counts"]["act_1"],
                act_2=n["act_counts"]["act_2"],
                act_3=n["act_counts"]["act_3"],
            ),
            color_index=n["color_index"],
        ) for n in payload["nodes"]],
        edges=[GraphEdge(
            source=e["source"],
            target=e["target"],
            weight=e["weight"],
        ) for e in payload["edges"]],
    )


@router.post("/upload/compare", response_model=CompareUploadResponse)
async def upload_compare(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
):
    _evict_stale_sessions()

    results = await asyncio.gather(
        _parse_file(file_a),
        _parse_file(file_b),
        return_exceptions=True,
    )

    def extract_result(result):
        if isinstance(result, Exception):
            detail = getattr(result, "detail", {})
            return None, "error", [], ErrorDetail(
                error_code=detail.get("error_code", "INTERNAL_ERROR"),
                message=detail.get("message", str(result)),
            )
        script_data, session_id = result
        char_list = sorted(
            script_data.characters.keys(),
            key=lambda c: script_data.characters[c],
            reverse=True,
        )
        return session_id, "parsed", char_list, None

    sid_a, status_a, chars_a, err_a = extract_result(results[0])
    sid_b, status_b, chars_b, err_b = extract_result(results[1])

    return CompareUploadResponse(
        session_a=sid_a,
        session_b=sid_b,
        status_a=status_a,
        status_b=status_b,
        character_list_a=chars_a,
        character_list_b=chars_b,
        error_a=err_a,
        error_b=err_b,
    )
"""
CSV export endpoints for ArcGIS — one per Supabase table.

All endpoints query Supabase live on every request.
No caching — changes in Supabase are reflected immediately.

Endpoints:
  GET /export/projects.csv
  GET /export/meeting_types.csv
  GET /export/meetings.csv
  GET /export/locations.csv
  GET /export/documents.csv
"""
import csv
import io
from fastapi import APIRouter
from fastapi.responses import Response
from app.db import get_client

router = APIRouter(prefix="/export", tags=["Export"])


def _csv_response(rows: list[dict], filename: str) -> Response:
    """Generic helper — writes any list of flat dicts to CSV."""
    if not rows:
        return Response(content="", media_type="text/csv")

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )


@router.get("/projects.csv", summary="Export projects table")
def export_projects():
    rows = get_client().table("projects").select("*").execute().data
    return _csv_response(rows, "projects.csv")


@router.get("/meeting_types.csv", summary="Export meeting_types table")
def export_meeting_types():
    rows = get_client().table("meeting_types").select("*").execute().data
    return _csv_response(rows, "meeting_types.csv")


@router.get("/meetings.csv", summary="Export meetings table")
def export_meetings():
    rows = get_client().table("meetings").select("*").execute().data
    return _csv_response(rows, "meetings.csv")


@router.get("/locations.csv", summary="Export locations table with project info")
def export_locations():
    raw = (
        get_client()
        .table("locations")
        .select("location_id, location_name, location_type, address, description, latitude, longitude, projects(project_name, status)")
        .execute()
        .data
    )
    rows = []
    for row in raw:
        project = row.pop("projects") or {}
        rows.append({
            **row,
            "project_name": project.get("project_name"),
            "project_status": project.get("status"),
        })
    return _csv_response(rows, "locations.csv")


@router.get("/documents.csv", summary="Export documents table")
def export_documents():
    rows = get_client().table("documents").select("*").execute().data
    return _csv_response(rows, "documents.csv")

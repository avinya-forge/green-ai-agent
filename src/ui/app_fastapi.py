"""
Green AI Agent Dashboard (FastAPI)

This module initializes the FastAPI application and Socket.IO server
for the migration from Flask/Eventlet.
"""

import socketio
from fastapi import FastAPI, Request, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Any, List, Optional
import os
import sys

from src.ui.schemas import ScanRequest
import threading
import asyncio

from src.core.domain import ProjectSummaryDTO, ProjectDTO, ProjectComparisonDTO
from src.utils.metrics import calculate_projects_grade
from src.core.scanner import Scanner
from src.core.calibration import CalibrationAgent
from src.core.export import OUTPUT_DIR, CSVExporter, HTMLReporter
from src.core.telemetry.service import TelemetryService
import src.ui.state as state

from src.ui.middleware.security import SecurityHeadersMiddleware
from src.ui.middleware.rate_limit import RateLimitMiddleware

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize default project and trigger scan if needed."""
    print("Starting up Green-AI Agent Dashboard...", file=sys.stderr)

    # Ensure globals are initialized
    pm = state.get_project_manager()
    hm = state.get_history_manager()
    state.get_standards_registry()
    state.get_remediation_engine()

    try:
        default_project = pm.get_project("Green-AI Agent")
        # Force use the local path for the default project
        # root_dir is 3 levels up from this file (src/ui/app_fastapi.py -> src/ui -> src -> root)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        if not default_project:
            pm.add_project(
                name="Green-AI Agent",
                repo_url=root_dir,
                branch="main",
                language="python",
                is_system=True
            )
            print(f"Initialized default project at {root_dir}", file=sys.stderr)

        # Trigger initial scan in background if last_scan is None
        default_project = pm.get_project("Green-AI Agent")
        if default_project and not default_project.last_scan:
            print("Triggering initial background scan for Green-AI Agent...", file=sys.stderr)

            # Use the existing background scan logic but simplified for internal use
            loop = asyncio.get_running_loop()

            def initial_scan():
                try:
                    # Bridge to async emit
                    def progress_cb(msg, pct):
                        asyncio.run_coroutine_threadsafe(broadcast_progress(msg, pct), loop)

                    scanner = Scanner(language="python")
                    results = scanner.scan(root_dir, progress_callback=progress_cb)

                    state.set_last_scan_results(results)
                    hm.add_scan("Green-AI Agent", results)
                    pm.update_project_scan("Green-AI Agent", results['issues'], results.get('total_emissions', 0))

                    print("Initial scan completed.", file=sys.stderr)
                    asyncio.run_coroutine_threadsafe(broadcast_progress("Scan complete!", 100), loop)
                    asyncio.run_coroutine_threadsafe(sio.emit('scan_finished', {'project_name': "Green-AI Agent"}), loop)

                except Exception as e:
                    print(f"Initial scan failed: {e}", file=sys.stderr)

            thread = threading.Thread(target=initial_scan)
            thread.daemon = True
            thread.start()

    except Exception as e:
        print(f"Warning: Could not initialize default project: {e}", file=sys.stderr)

    yield


# Initialize FastAPI app
app = FastAPI(title="Green-AI Agent Dashboard", lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {exc}", file=sys.stderr)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# Add middleware
# Note: Middleware is added in reverse order (LIFO).
# The last middleware added is the first one to handle the request.
# We want SecurityHeaders to be outermost (first to handle request, last to handle response)
# so it can add headers to all responses, including 429s from RateLimit.
app.add_middleware(RateLimitMiddleware, limit=100, window=60)
app.add_middleware(SecurityHeadersMiddleware)

# Initialize Socket.IO server (ASGI mode)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Wrap FastAPI app with Socket.IO ASGI app
app_asgi = socketio.ASGIApp(sio, other_asgi_app=app)

# Templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


# Helpers
async def broadcast_progress(message: str, percentage: int):
    """Broadcast scan progress to all connected clients."""
    await sio.emit('scan_progress', {'message': message, 'percentage': percentage})

# Routes


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if state.last_scan_results:
        insights = state.generate_insights(state.last_scan_results)
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "results": state.last_scan_results,
                "insights": insights,
                "charts": state.last_charts
            }
        )
    else:
        # Show enhanced landing page with stats
        pm = state.get_project_manager()
        projects = pm.list_projects()
        total_violations = sum(p.latest_violations for p in projects)
        avg_grade = calculate_projects_grade(projects) if projects else "N/A"
        recent_projects = sorted(projects, key=lambda p: p.last_scan or "", reverse=True)[:5]

        return templates.TemplateResponse(
            "landing.html",
            {
                "request": request,
                "projects": projects,
                "total_violations": total_violations,
                "avg_grade": avg_grade,
                "recent_projects": recent_projects,
                "project_count": len(projects)
            }
        )


@app.get("/api/charts")
async def api_charts() -> Any:
    return state.last_charts or {}


@app.get("/api/results")
async def api_results() -> Any:
    return state.last_scan_results or {}


@app.get("/api/health")
async def api_health() -> Any:
    return {"status": "ok"}


@app.get("/api/telemetry")
async def api_telemetry() -> Any:
    try:
        service = TelemetryService()
        return {
            'status': 'ok',
            'events': service.get_all_events()
        }
    except Exception as e:
        print(f"Error in api_telemetry: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/standards")
async def api_standards_list() -> Any:
    return state.get_standards_registry().list_standards()


@app.get("/api/standards/{standard_name}/rules")
async def api_standard_rules(standard_name: str) -> Any:
    registry = state.get_standards_registry()
    if standard_name in registry.standards:
        rules = registry.standards[standard_name]
        return {
            'standard': standard_name,
            'rule_count': len(rules),
            'rules': [{'id': r.id, 'name': r.name, 'severity': r.severity} for r in rules]
        }
    raise HTTPException(status_code=404, detail="Standard not found")


@app.get("/api/projects")
async def api_projects_list() -> Any:
    pm = state.get_project_manager()
    projects = pm.list_projects()

    # Use DTO
    projects_data = [ProjectSummaryDTO.from_project(p).model_dump() for p in projects]

    return {
        'status': 'ok',
        'total_projects': len(projects_data),
        'projects': projects_data,
        'summary': {
            'total_violations': sum(p['violation_count'] for p in projects_data),
            'total_high_violations': sum(p['high_violations'] for p in projects_data),
            'average_grade': calculate_projects_grade(projects),
            'combined_emissions': sum(p['total_emissions'] for p in projects_data),
        }
    }


@app.get("/api/projects/comparison")
async def api_projects_comparison(projects: List[str] = Query(None)) -> Any:
    if not projects or len(projects) == 0:
        raise HTTPException(status_code=400, detail="No projects specified. Use ?projects=name1&projects=name2")

    if len(projects) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 projects can be compared at once")

    comparison_data = []
    pm = state.get_project_manager()
    for project_name in projects:
        project = pm.get_project(project_name)
        if project:
            comparison_data.append(ProjectComparisonDTO.from_project(project).model_dump())

    if not comparison_data:
        raise HTTPException(status_code=404, detail="No valid projects found")

    return {
        'status': 'ok',
        'comparison_count': len(comparison_data),
        'projects': comparison_data
    }


@app.get("/api/projects/{project_name}")
async def api_project_detail(project_name: str) -> Any:
    pm = state.get_project_manager()
    project = pm.get_project(project_name)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        'status': 'ok',
        'project': ProjectDTO.from_project(project).model_dump()
    }


@app.get("/api/history")
async def api_get_history(project: str, days: Optional[int] = None) -> Any:
    if not project:
        raise HTTPException(status_code=400, detail="project parameter required")

    try:
        scans = state.get_history_manager().get_project_history(project, days=days)
        return {
            'project': project,
            'scans': [s.to_dict() for s in scans],
            'count': len(scans)
        }
    except Exception as e:
        print(f"Error in api_get_history: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/trending")
async def api_get_trending(project: str, days: Optional[int] = None) -> Any:
    if not project:
        raise HTTPException(status_code=400, detail="project parameter required")

    try:
        trending = state.get_history_manager().get_trending_data(project, days=days)
        return {
            'project': project,
            'trend': trending['trend'],
            'details': trending,
            'grade_improvement': trending.get('grade_improvement', 'N/A')
        }
    except Exception as e:
        print(f"Error in api_get_trending: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/compare")
async def api_compare_scans(
    project: str,
    scan1: int = -2,
    scan2: int = -1
) -> Any:
    if not project:
        raise HTTPException(status_code=400, detail="project parameter required")

    try:
        hm = state.get_history_manager()
        scans = hm.get_project_history(project)

        if len(scans) < 2:
            raise HTTPException(status_code=400, detail="Not enough scans to compare")

        scan1_obj = scans[scan1] if scan1 < len(scans) else scans[0]
        scan2_obj = scans[scan2] if scan2 < len(scans) else scans[-1]

        comparison = hm.compare_scans(scan1_obj, scan2_obj)

        return {
            'project': project,
            'scan1_timestamp': scan1_obj.timestamp,
            'scan2_timestamp': scan2_obj.timestamp,
            'new_violations': comparison['changes']['new_violations'],
            'fixed_violations': comparison['changes']['fixed_violations'],
            'grade_change': comparison.get('grade_change', 'N/A'),
            'details': comparison.get('details', {})
        }
    except IndexError:
        raise HTTPException(status_code=400, detail="Scan index out of range")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in api_compare_scans: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/scan")
async def api_scan(request: ScanRequest):
    project_name = request.project_name
    language = request.language
    git_url = request.git_url
    path = request.path

    if not git_url and not path:
        raise HTTPException(status_code=400, detail="Either git_url or path is required")

    pm = state.get_project_manager()
    existing = pm.get_project(project_name)
    if not existing:
        pm.add_project(project_name, repo_url=git_url or path, language=language)

    # We need to run the scan in a background thread because it is blocking
    # and we want to emit progress events.

    # Get the current event loop to schedule async tasks from the thread
    loop = asyncio.get_running_loop()

    def run_background_scan():
        try:
            # Helper to bridge sync callback to async emit
            def progress_cb(msg, pct):
                asyncio.run_coroutine_threadsafe(broadcast_progress(msg, pct), loop)

            asyncio.run_coroutine_threadsafe(broadcast_progress("Starting background scan...", 5), loop)

            scan_path = path or git_url
            scanner = Scanner(language=language)
            results = scanner.scan(scan_path, progress_callback=progress_cb)

            state.set_last_scan_results(results)
            state.get_history_manager().add_scan(project_name, results)

            asyncio.run_coroutine_threadsafe(broadcast_progress("Scan complete!", 100), loop)
            asyncio.run_coroutine_threadsafe(sio.emit('scan_finished', {'project_name': project_name}), loop)

        except Exception as e:
            print(f"Background scan error: {e}", file=sys.stderr)
            asyncio.run_coroutine_threadsafe(broadcast_progress("Error: Internal Server Error", 0), loop)
            asyncio.run_coroutine_threadsafe(sio.emit('scan_error', {'error': 'Internal Server Error'}), loop)

    thread = threading.Thread(target=run_background_scan)
    thread.daemon = True
    thread.start()

    return {
        'status': 'ok',
        'message': f'Scan initiated for {project_name}',
        'project_name': project_name,
        'scan_type': 'git' if git_url else 'local',
        'language': language
    }


@app.delete("/api/projects/{project_name}")
async def api_delete_project(project_name: str):
    pm = state.get_project_manager()
    project = pm.get_project(project_name)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_name} not found")

    if project.is_system:
        raise HTTPException(status_code=403, detail=f"Cannot delete system project: {project_name}")

    try:
        pm.remove_project(project_name)
        return {
            'status': 'ok',
            'message': f'Project {project_name} deleted'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/projects/{project_name}/rescan")
async def api_rescan_project(project_name: str):
    project = state.get_project_manager().get_project(project_name)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        'status': 'ok',
        'message': f'Rescan initiated for {project_name}',
        'project_name': project_name,
        'url': project.repo_url,
        'language': project.language
    }


@app.post("/api/projects/{project_name}/clear")
async def api_clear_project(project_name: str):
    pm = state.get_project_manager()
    project = pm.get_project(project_name)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        project.latest_violations = 0
        project.total_emissions = 0.0
        pm._save_projects()
        return {
            'status': 'ok',
            'message': f'Project {project_name} cleared and ready for rescan'
        }
    except Exception as e:
        print(f"Error in api_clear_project: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Standards Management


@app.post("/api/standards/{standard_name}/enable")
async def api_enable_standard(standard_name: str):
    state.get_standards_registry().enable_standard(standard_name)
    return {'status': 'ok', 'message': f'Standard {standard_name} enabled'}


@app.post("/api/standards/{standard_name}/disable")
async def api_disable_standard(standard_name: str):
    state.get_standards_registry().disable_standard(standard_name)
    return {'status': 'ok', 'message': f'Standard {standard_name} disabled'}


@app.post("/api/rules/{rule_id}/enable")
async def api_enable_rule(rule_id: str):
    state.get_standards_registry().enable_rule(rule_id)
    return {'status': 'ok', 'message': f'Rule {rule_id} enabled'}


@app.post("/api/rules/{rule_id}/disable")
async def api_disable_rule(rule_id: str):
    state.get_standards_registry().disable_rule(rule_id)
    return {'status': 'ok', 'message': f'Rule {rule_id} disabled'}

# Remediation


@app.get("/api/remediation/preview")
async def api_remediation_preview(
    project: str = Query(...),
    file: str = Query(...),
    line: int = Query(...),
    issue_id: str = Query(...)
):
    try:
        # Read the original file content
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        engine = state.get_remediation_engine()
        diff = engine.get_diff(file, content, line, issue_id)
        description = engine.get_suggestion(issue_id)

        return {
            'status': 'ok',
            'diff': diff or "No automated fix available.",
            'description': description
        }
    except Exception as e:
        print(f"Error in api_remediation_preview: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Calibration


@app.api_route("/api/calibrate", methods=["GET", "POST"])
async def api_calibrate(request: Request):
    try:
        agent = CalibrationAgent()
        if request.method == 'POST':
            profile = agent.run_calibration()
        else:
            profile = agent.profile

        return {
            'status': 'ok',
            'profile': profile
        }
    except Exception as e:
        print(f"Error in api_calibrate: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Export


def _handle_export(exporter_cls, mime_type, file_extension, project_name='Scan'):
    if not state.last_scan_results:
        raise HTTPException(status_code=400, detail="No scan results available. Run a scan first.")

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / f'green-ai-report-{project_name}.{file_extension}'
        exporter = exporter_cls(output_path=str(output_path))
        exporter.export(state.last_scan_results, project_name)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if output_path.exists():
            output_path.unlink()

        headers = {
            'Content-Type': f'{mime_type}; charset=utf-8'
        }
        if file_extension == 'csv':
            headers['Content-Disposition'] = f'attachment; filename="{output_path.name}"'

        return Response(content=content, media_type=mime_type, headers=headers)

    except Exception as e:
        print(f"Error in _handle_export: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/export/csv")
async def api_export_csv(project: str = 'Scan'):
    return _handle_export(CSVExporter, 'text/csv', 'csv', project)


@app.get("/api/export/html")
async def api_export_html(project: str = 'Scan'):
    return _handle_export(HTMLReporter, 'text/html', 'html', project)

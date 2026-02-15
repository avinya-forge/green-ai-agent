# Eventlet Migration Plan

## Context
The current implementation relies on `eventlet` for asynchronous support in `Flask-SocketIO`. This dependency introduces significant complexity due to monkey-patching of the standard library, which conflicts with `multiprocessing` used in the `Scanner` component. Additionally, `eventlet` is less actively maintained compared to modern asyncio-based solutions.

## Current Architecture
- **Framework**: Flask
- **WebSocket**: Flask-SocketIO
- **Async Mode**: Eventlet (`async_mode='eventlet'`)
- **Server**: `socketio.run(app)` (wraps eventlet's WSGI server)
- **Concurrency**: Green threads via monkey-patching.

## Proposed Architecture
- **Framework**: FastAPI
- **WebSocket**: Python-SocketIO (ASGI mode)
- **Async Mode**: Native Asyncio
- **Server**: Uvicorn (ASGI server)
- **Concurrency**: Standard Python `async/await`.

## Benefits
1.  **Removal of Monkey-Patching**: Eliminates conflicts with `multiprocessing` and standard library modules.
2.  **Performance**: Uvicorn is a high-performance ASGI server.
3.  **Type Safety**: FastAPI leverages Pydantic for request validation (aligning with our recent Pydantic adoption).
4.  **Modern Ecosystem**: Asyncio is the standard for Python concurrency.

## Migration Steps

### Phase 1: Preparation
1.  Add `fastapi`, `uvicorn`, and `python-socketio` to `requirements.txt`.
2.  Remove `eventlet` and `flask-socketio` (once migration is complete).

### Phase 2: Implementation (Parallel)
1.  Create `src/ui/app_fastapi.py` as the new entry point.
2.  Initialize `socketio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')`.
3.  Wrap it with `app = socketio.ASGIApp(socketio, other_asgi_app=fastapi_app)`.

### Phase 3: Porting
1.  **HTTP Routes**: Convert Flask `@app.route` to FastAPI `@app.get` / `@app.post`.
    -   Use Pydantic models (DTOs) for request/response schemas.
    -   Replace `jsonify()` with direct dictionary/model returns.
2.  **WebSockets**:
    -   Convert `@socketio.on` handlers to async functions: `@sio.event async def connect(sid, environ): ...`.
    -   Update `broadcast_progress` to be an async function.
3.  **Templates**: Use `jinja2` directly or `fastapi.templating.Jinja2Templates`.

### Phase 4: Switchover
1.  Update `src/ui/server.py` to run Uvicorn.
2.  Update `src/cli.py` to launch the new server.
3.  Verify all tests pass.
4.  Remove old Flask code.

## Estimated Effort
-   **Setup**: 2h
-   **Porting Routes**: 6h
-   **Porting WebSockets**: 4h
-   **Testing & Verification**: 4h
-   **Total**: ~16h (2 Sprints)

"""
Green AI Agent Dashboard (FastAPI)

This module initializes the FastAPI application and Socket.IO server
for the migration from Flask/Eventlet.
"""

import socketio
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI(title="Green-AI Agent Dashboard")

# Initialize Socket.IO server (ASGI mode)
# cors_allowed_origins='*' is used for development convenience
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Wrap FastAPI app with Socket.IO ASGI app
app_asgi = socketio.ASGIApp(sio, other_asgi_app=app)

# Note: Static files and templates mounting will happen in later phases

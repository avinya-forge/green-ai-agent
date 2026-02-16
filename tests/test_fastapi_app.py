"""
Tests for the new FastAPI application scaffolding.
"""
import pytest
from socketio import ASGIApp

def test_fastapi_app_initialization():
    """Verify that the FastAPI app and Socket.IO ASGI app are initialized correctly."""
    from src.ui.app_fastapi import app, sio, app_asgi

    assert app.title == "Green-AI Agent Dashboard"
    assert sio.async_mode == 'asgi'
    assert isinstance(app_asgi, ASGIApp)

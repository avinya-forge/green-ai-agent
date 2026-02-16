"""
Green AI Agent Dashboard Server

This module acts as the entry point for the dashboard application.
It uses Uvicorn to serve the FastAPI application.
"""

def run_dashboard():
    """Run the Green AI Agent Dashboard"""
    import uvicorn
    import sys
    from src.ui.app_fastapi import app_asgi
    
    import logging
    from pathlib import Path
    
    # Configure logging to output/logs
    logs_dir = Path(__file__).parent.parent.parent / 'output' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting server on http://127.0.0.1:5000", file=sys.stderr)
    uvicorn.run(app_asgi, host='127.0.0.1', port=5000, log_level="info")

if __name__ == '__main__':
    run_dashboard()

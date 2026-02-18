import pytest
from src.core.detectors import detect_violations

def test_async_blocking_io_time_sleep():
    code = """
import asyncio
import time

async def my_task():
    print("Starting")
    time.sleep(1)  # Blocking!
    print("Done")
"""
    violations = detect_violations(code, "test.py", "python")

    assert any(v['id'] == 'blocking_io_in_async' for v in violations)
    assert any(v['message'].startswith('Blocking I/O "time.sleep()"') for v in violations)

def test_async_blocking_io_requests():
    code = """
import asyncio
import requests

async def fetch_data():
    requests.get("https://example.com")  # Blocking!
"""
    violations = detect_violations(code, "test.py", "python")

    assert any(v['id'] == 'blocking_io_in_async' for v in violations)
    assert any(v['message'].startswith('Blocking I/O "requests.get()"') for v in violations)

def test_async_blocking_io_open():
    code = """
async def read_file():
    f = open("data.txt", "r")  # Blocking!
    content = f.read()
    f.close()
"""
    violations = detect_violations(code, "test.py", "python")

    assert any(v['id'] == 'blocking_io_in_async' for v in violations)
    assert any(v['message'].startswith('Blocking I/O "open()"') for v in violations)

def test_async_no_blocking_io():
    code = """
import asyncio
import aiohttp

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://example.com") as resp:
            data = await resp.text()
"""
    violations = detect_violations(code, "test.py", "python")

    assert not any(v['id'] == 'blocking_io_in_async' for v in violations)

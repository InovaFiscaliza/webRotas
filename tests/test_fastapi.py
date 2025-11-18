"""Simple test script for FastAPI endpoints"""

import subprocess
import time
import requests


def test_fastapi():
    """Test FastAPI endpoints"""

    # Start the server
    print("[Test] Starting FastAPI server...")
    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "webrotas.main:app",
            "--port",
            "5003",
            "--host",
            "127.0.0.1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/home/ronaldo/Work/webRotas/src",
    )

    time.sleep(5)  # Give server time to start

    try:
        # Test 1: Health check
        print("\n[Test 1] Testing health check endpoint...")
        try:
            response = requests.get("http://127.0.0.1:5003/ok?sessionId=test")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            assert response.status_code == 200
            assert response.text == '"ok"'
            print("  ✓ PASSED")
        except Exception as e:
            print(f"  ✗ FAILED: {e}")

        # Test 2: Missing sessionId
        print("\n[Test 2] Testing missing sessionId (should fail)...")
        try:
            response = requests.get("http://127.0.0.1:5003/ok")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
            assert (
                response.status_code == 422
            )  # FastAPI returns 422 for missing query params
            print("  ✓ PASSED")
        except Exception as e:
            print(f"  ✗ FAILED: {e}")

        # Test 3: OpenAPI docs
        print("\n[Test 3] Testing OpenAPI documentation...")
        try:
            response = requests.get("http://127.0.0.1:5003/docs")
            print(f"  Status: {response.status_code}")
            assert response.status_code == 200
            assert (
                "swagger" in response.text.lower() or "openapi" in response.text.lower()
            )
            print("  ✓ PASSED - API docs available")
        except Exception as e:
            print(f"  ✗ FAILED: {e}")

        # Test 4: OpenAPI schema
        print("\n[Test 4] Testing OpenAPI schema...")
        try:
            response = requests.get("http://127.0.0.1:5003/openapi.json")
            print(f"  Status: {response.status_code}")
            schema = response.json()
            print(f"  Endpoints found: {len(schema.get('paths', {}))}")
            print(f"  Paths: {list(schema.get('paths', {}).keys())}")
            assert response.status_code == 200
            assert "/process" in schema.get("paths", {})
            assert "/ok" in schema.get("paths", {})
            print("  ✓ PASSED - OpenAPI schema correct")
        except Exception as e:
            print(f"  ✗ FAILED: {e}")

        print("\n[Test] All basic tests completed!")

    finally:
        # Kill the server
        print("\n[Test] Shutting down server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        print("[Test] Server stopped")


if __name__ == "__main__":
    test_fastapi()

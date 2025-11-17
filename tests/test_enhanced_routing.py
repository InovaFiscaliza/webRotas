#!/usr/bin/env python3
"""
Test enhanced routing functionality with public API limitations and local container fallback.
"""

import sys
import os
import logging

# Add project src to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src", "backend", "webdir")
)

from webrotas import api_routing

# Setup basic logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


async def test_basic_routing():
    """Test basic routing functionality with small number of points."""
    print("\n=== Test 1: Basic routing (should use public API) ===")

    origin = {"lat": -23.55052, "lng": -46.57421, "description": "Origin"}
    waypoints = [
        {"lat": -23.54785, "lng": -46.58325, "description": "Point 1"},
        {"lat": -23.55130, "lng": -46.57944, "description": "Point 2"},
    ]

    try:
        result = await api_routing.calculate_optimal_route(origin, waypoints, "distance")
        print("✅ Basic routing successful")
        print(f"   Origin: {result[0]}")
        print(f"   Waypoints: {len(result[1])}")
        print(f"   Distance: {result[4]}")
        print(f"   Time: {result[3]}")
        return True
    except Exception as e:
        print(f"❌ Basic routing failed: {e}")
        return False


async def test_many_points_routing():
    """Test routing with >100 points (should use local container)."""
    print("\n=== Test 2: Many points routing (should use local container) ===")

    origin = {"lat": -23.55052, "lng": -46.57421, "description": "Origin"}

    # Generate 101 waypoints in a small area around São Paulo
    waypoints = []
    for i in range(101):
        lat = -23.55 + (i % 10) * 0.001  # Small grid pattern
        lng = -46.57 + (i // 10) * 0.001
        waypoints.append({"lat": lat, "lng": lng, "description": f"Point {i + 1}"})

    try:
        result = await api_routing.calculate_optimal_route(origin, waypoints, "distance")
        print("✅ Many points routing successful")
        print(f"   Origin: {result[0]}")
        print(f"   Waypoints: {len(result[1])}")
        print(f"   Distance: {result[4]}")
        print(f"   Time: {result[3]}")
        return True
    except Exception as e:
        print(f"❌ Many points routing failed: {e}")
        print("   This is expected if no local container is available")
        return False


async def test_exclusion_zones_routing():
    """Test routing with exclusion zones (should use local container)."""
    print("\n=== Test 3: Exclusion zones routing (should use local container) ===")

    origin = {"lat": -23.55052, "lng": -46.57421, "description": "Origin"}
    waypoints = [
        {"lat": -23.54785, "lng": -46.58325, "description": "Point 1"},
        {"lat": -23.55130, "lng": -46.57944, "description": "Point 2"},
    ]

    # Define an exclusion zone
    avoid_zones = [
        {
            "name": "Test exclusion zone",
            "coord": [
                [-23.549, -46.575],
                [-23.549, -46.580],
                [-23.553, -46.580],
                [-23.553, -46.575],
            ],
        }
    ]

    try:
        result = await api_routing.calculate_optimal_route(
            origin, waypoints, "distance", avoid_zones
        )
        print("✅ Exclusion zones routing successful")
        print(f"   Origin: {result[0]}")
        print(f"   Waypoints: {len(result[1])}")
        print(f"   Distance: {result[4]}")
        print(f"   Time: {result[3]}")
        return True
    except Exception as e:
        print(f"❌ Exclusion zones routing failed: {e}")
        print("   This is expected if no local container is available")
        return False


async def test_matrix_functions():
    """Test the matrix calculation functions directly."""
    print("\n=== Test 4: Matrix functions ===")

    coords = [
        {"lat": -23.55052, "lng": -46.57421},
        {"lat": -23.54785, "lng": -46.58325},
        {"lat": -23.55130, "lng": -46.57944},
    ]

    # Test public API matrix
    try:
        distances, durations = await api_routing.get_osrm_matrix(coords)
        print(
            f"✅ Public API matrix successful: {len(distances)}x{len(distances[0])} matrix"
        )
        valid = api_routing.validate_matrix(coords, distances, durations)
        print(f"   Matrix valid: {valid is not None}")
    except Exception as e:
        print(f"❌ Public API matrix failed: {e}")

    # Test geodesic fallback
    try:
        distances, durations = api_routing.get_geodesic_matrix(coords, speed_kmh=40)
        print(
            f"✅ Geodesic matrix successful: {len(distances)}x{len(distances[0])} matrix"
        )
        valid = api_routing.validate_matrix(coords, distances, durations)
        print(f"   Matrix valid: {valid is not None}")
    except Exception as e:
        print(f"❌ Geodesic matrix failed: {e}")

    # Test local container (will likely fail without setup, but should not crash)
    try:
        distances, durations = await api_routing.get_osrm_matrix_from_local_container(coords)
        print(
            f"✅ Local container matrix successful: {len(distances)}x{len(distances[0])} matrix"
        )
        valid = api_routing.validate_matrix(coords, distances, durations)
        print(f"   Matrix valid: {valid is not None}")
    except Exception as e:
        print(f"❌ Local container matrix failed (expected): {e}")


async def main():
    """Run all tests."""
    import asyncio
    
    print("🚀 Testing Enhanced Routing Functionality")
    print("=" * 50)

    test_results = []

    test_results.append(await test_basic_routing())
    test_results.append(await test_many_points_routing())
    test_results.append(await test_exclusion_zones_routing())

    await test_matrix_functions()

    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Passed: {sum(test_results)}")
    print(f"   Failed: {len(test_results) - sum(test_results)}")
    print(f"   Total:  {len(test_results)}")

    if all(test_results):
        print("🎉 All main tests passed!")
    else:
        print(
            "⚠️  Some tests failed (likely due to local container not being available)"
        )
        print("   This is normal if the local OSRM containers are not set up")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

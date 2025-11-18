#!/usr/bin/env python
"""
Test script to verify segment-based alternatives integration.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from webrotas.api_routing import get_osrm_route, request_osrm
from webrotas.segment_alternatives import get_alternatives_for_multipoint_route


async def test_segment_alternatives():
    """Test segment-based alternatives with a simple 3-waypoint route."""
    
    # Create simple test coordinates (3 waypoints)
    coords = [
        {"lat": -23.5505, "lng": -46.5742, "description": "Point A"},
        {"lat": -23.5480, "lng": -46.5833, "description": "Point B"},
        {"lat": -23.5510, "lng": -46.5794, "description": "Point C"},
    ]
    
    # Simple test avoid zone
    avoid_zones = [
        {
            "name": "Test Zone",
            "coord": [
                [-46.5800, -23.5490],
                [-46.5800, -23.5500],
                [-46.5810, -23.5500],
                [-46.5810, -23.5490],
            ]
        }
    ]
    
    print("Testing segment-based alternatives...")
    print(f"  Coordinates: {len(coords)} waypoints")
    print(f"  Avoid zones: {len(avoid_zones)} zone(s)")
    
    try:
        # Test the segment-based alternatives function directly
        alternatives, error = await get_alternatives_for_multipoint_route(
            coordinates=coords,
            request_osrm_fn=request_osrm,
            avoid_zones=avoid_zones,
            num_alternatives=3,
            max_routes=3,
        )
        
        if error:
            print(f"✗ Error occurred: {error}")
            return False
        
        if alternatives:
            print(f"✓ Successfully generated {len(alternatives)} alternative routes")
            for i, alt in enumerate(alternatives):
                print(f"  Route {i+1}:")
                print(f"    - Distance: {alt.get('distance', 0):.0f}m")
                print(f"    - Duration: {alt.get('duration', 0):.0f}s")
                print(f"    - Zone intersections: {alt.get('zone_intersections', 0)}")
                print(f"    - Penalty score: {alt.get('penalty_score', 0):.3f}")
            return True
        else:
            print("✗ No alternatives generated")
            return False
            
    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_osrm_route_with_avoid_zones():
    """Test get_osrm_route with avoid zones and multiple waypoints."""
    
    print("\nTesting get_osrm_route with avoid zones...")
    
    coords = [
        {"lat": -23.5505, "lng": -46.5742, "description": "Point A"},
        {"lat": -23.5480, "lng": -46.5833, "description": "Point B"},
        {"lat": -23.5510, "lng": -46.5794, "description": "Point C"},
    ]
    
    avoid_zones = [
        {
            "name": "Test Zone",
            "coord": [
                [-46.5800, -23.5490],
                [-46.5800, -23.5500],
                [-46.5810, -23.5500],
                [-46.5810, -23.5490],
            ]
        }
    ]
    
    order = [0, 1, 2]  # Visit in order
    
    try:
        data, ordered_coords = await get_osrm_route(
            coords, order, avoid_zones=avoid_zones
        )
        
        if data.get("routes"):
            print(f"✓ Successfully retrieved {len(data['routes'])} route(s)")
            for i, route in enumerate(data["routes"]):
                print(f"  Route {i+1}:")
                print(f"    - Distance: {route.get('distance', 0):.0f}m")
                print(f"    - Duration: {route.get('duration', 0):.0f}s")
                if "penalties" in route:
                    penalties = route["penalties"]
                    print(f"    - Zone intersections: {penalties.get('zone_intersections', 0)}")
                    print(f"    - Penalty score: {penalties.get('penalty_score', 0):.3f}")
            return True
        else:
            print("✗ No routes returned")
            return False
            
    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Segment-Based Alternatives Integration Test")
    print("=" * 60)
    
    result1 = await test_segment_alternatives()
    result2 = await test_get_osrm_route_with_avoid_zones()
    
    print("\n" + "=" * 60)
    if result1 and result2:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

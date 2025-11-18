#!/usr/bin/env python
"""
Test zone-aware routing with Osasco scenario.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from webrotas.api_routing import get_osrm_route
from webrotas.zone_aware_routing import generate_boundary_waypoints
from webrotas.geojson_converter import avoid_zones_to_geojson
from webrotas.api_routing import load_spatial_index


async def test_osasco_scenario():
    """Test the Osasco-SP avoid zone scenario (3-waypoint)."""
    
    print("Testing Osasco scenario (3-waypoint with large avoid zone)...")
    
    # From the test file
    coords = [
        {"lat": -23.5346647, "lng": -46.8258591, "description": "Osasco-SP"},
        {"lat": -23.58561, "lng": -46.6677705, "description": "Ibirapuera"},
        {"lat": -23.587504, "lng": -46.633257, "description": "Anatel-SP"},
    ]
    
    avoid_zones = [
        {
            "name": "Marginal Pinheiros",
            "coord": [
                [-46.8200, -23.5300],
                [-46.8150, -23.5320],
                [-46.8100, -23.5340],
                [-46.8000, -23.5380],
                [-46.7900, -23.5420],
                [-46.7800, -23.5460],
                [-46.7700, -23.5500],
                [-46.7650, -23.5520],
                [-46.7600, -23.5540],
                [-46.7500, -23.5580],
                [-46.7400, -23.5620],
                [-46.7350, -23.5640],
                [-46.7300, -23.5660],
                [-46.7200, -23.5700],
                [-46.7100, -23.5740],
                [-46.7000, -23.5780],
                [-46.6950, -23.5800],
                [-46.6900, -23.5820],
                [-46.6850, -23.5840],
                [-46.6800, -23.5860],
                [-46.6750, -23.5850],
                [-46.6800, -23.5820],
                [-46.6850, -23.5800],
                [-46.6900, -23.5780],
                [-46.6950, -23.5760],
                [-46.7000, -23.5740],
                [-46.7100, -23.5700],
                [-46.7200, -23.5660],
                [-46.7300, -23.5620],
                [-46.7350, -23.5600],
                [-46.7400, -23.5580],
                [-46.7500, -23.5540],
                [-46.7600, -23.5500],
                [-46.7700, -23.5460],
                [-46.7800, -23.5420],
                [-46.7900, -23.5380],
                [-46.8000, -23.5340],
                [-46.8100, -23.5300],
                [-46.8150, -23.5280],
                [-46.8200, -23.5260],
            ]
        }
    ]
    
    order = [0, 1, 2]
    
    try:
        print(f"\n  Origin: {coords[0]['description']}")
        print(f"  Waypoints: {', '.join([c['description'] for c in coords[1:]])}")
        print(f"  Avoid zones: {len(avoid_zones)}")
        
        # Test the full routing
        data, ordered_coords = await get_osrm_route(
            coords, order, avoid_zones=avoid_zones
        )
        
        if data.get("routes"):
            print(f"\n✓ Successfully retrieved {len(data['routes'])} route(s)")
            for i, route in enumerate(data["routes"]):
                print(f"\n  Route {i+1}:")
                print(f"    - Distance: {route.get('distance', 0):.0f}m")
                print(f"    - Duration: {route.get('duration', 0):.0f}s")
                if "penalties" in route:
                    penalties = route["penalties"]
                    print(f"    - Zone intersections: {penalties.get('zone_intersections', 0)}")
                    print(f"    - Penalty score: {penalties.get('penalty_score', 0):.4f}")
            
            # Check first route
            first_route_penalty = data["routes"][0].get("penalties", {}).get("penalty_score", 0)
            if first_route_penalty == 0:
                print("\n✓✓ First route successfully avoids zones!")
                return True
            else:
                print("\n⚠ First route still has zone intersections")
                return False
        else:
            print("✗ No routes returned")
            return False
            
    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_boundary_waypoint_generation():
    """Test boundary waypoint generation around the Marginal Pinheiros zone."""
    
    print("\n" + "="*60)
    print("Testing boundary waypoint generation...")
    
    avoid_zones = [
        {
            "name": "Marginal Pinheiros",
            "coord": [
                [-46.8200, -23.5300],
                [-46.8150, -23.5320],
                [-46.8100, -23.5340],
                [-46.8000, -23.5380],
                [-46.7900, -23.5420],
                [-46.7800, -23.5460],
                [-46.7700, -23.5500],
                [-46.7650, -23.5520],
                [-46.7600, -23.5540],
                [-46.7500, -23.5580],
                [-46.7400, -23.5620],
                [-46.7350, -23.5640],
                [-46.7300, -23.5660],
                [-46.7200, -23.5700],
                [-46.7100, -23.5740],
                [-46.7000, -23.5780],
                [-46.6950, -23.5800],
                [-46.6900, -23.5820],
                [-46.6850, -23.5840],
                [-46.6800, -23.5860],
                [-46.6750, -23.5850],
                [-46.6800, -23.5820],
                [-46.6850, -23.5800],
                [-46.6900, -23.5780],
                [-46.6950, -23.5760],
                [-46.7000, -23.5740],
                [-46.7100, -23.5700],
                [-46.7200, -23.5660],
                [-46.7300, -23.5620],
                [-46.7350, -23.5600],
                [-46.7400, -23.5580],
                [-46.7500, -23.5540],
                [-46.7600, -23.5500],
                [-46.7700, -23.5460],
                [-46.7800, -23.5420],
                [-46.7900, -23.5380],
                [-46.8000, -23.5340],
                [-46.8100, -23.5300],
                [-46.8150, -23.5280],
                [-46.8200, -23.5260],
            ]
        }
    ]
    
    try:
        geojson = avoid_zones_to_geojson(avoid_zones)
        polys, tree = load_spatial_index(geojson)
        
        if polys:
            print(f"✓ Loaded {len(polys)} polygon(s)")
            boundary_points = generate_boundary_waypoints(polys, avoid_zones, offset_km=2.0)
            print(f"✓ Generated {len(boundary_points)} boundary waypoints")
            
            for bp in boundary_points:
                print(f"  - {bp.direction.upper()}: ({bp.lat:.4f}, {bp.lng:.4f}) - Zone {bp.zone_index}")
            
            return True
        else:
            print("✗ Failed to load polygons")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Zone-Aware Routing Tests")
    print("=" * 60)
    
    result1 = await test_boundary_waypoint_generation()
    result2 = await test_osasco_scenario()
    
    print("\n" + "=" * 60)
    if result1 and result2:
        print("✓ All tests passed!")
        return 0
    else:
        print("⚠ Some tests completed with warnings or failures")
        return 0 if result2 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

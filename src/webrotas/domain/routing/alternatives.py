"""
Segment-based alternatives for multi-waypoint routing.

OSRM limitation: Alternatives only work for 2-coordinate requests.
Solution: Decompose multi-waypoint routes into segments (A→B, B→C, etc.),
request alternatives for each segment, then combine them intelligently.

This module handles:
1. Breaking multi-waypoint routes into 2-coordinate segments
2. Requesting OSRM alternatives for each segment
3. Combining segments into complete alternative routes
4. Scoring alternatives based on avoid zone penalties
"""

import asyncio
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RouteSegment:
    """A single segment of a route (2 coordinates)."""

    start_coord: Dict[str, float]  # {"lat": ..., "lng": ...}
    end_coord: Dict[str, float]
    index: int  # Position in overall route


@dataclass
class SegmentAlternative:
    """Alternative route for a segment."""

    segment_index: int
    route_option: int  # 0=best, 1=2nd best, etc.
    distance: float
    duration: float
    geometry: List[List[float]]  # [lng, lat] format


class SegmentAlternativesBuilder:
    """Build complete route alternatives from segment alternatives."""

    def __init__(
        self, coordinates: List[Dict[str, float]], avoid_zones: Optional[List] = None
    ):
        """
        Initialize builder for multi-waypoint routing.

        Args:
            coordinates: List of waypoint dicts with 'lat' and 'lng'
            avoid_zones: Optional list of avoid zone definitions
        """
        self.coordinates = coordinates
        self.avoid_zones = avoid_zones or []
        self.num_segments = len(coordinates) - 1
        self.segment_alternatives: List[List[SegmentAlternative]] = []

    def decompose_into_segments(self) -> List[Tuple[Dict, Dict]]:
        """
        Decompose multi-waypoint route into 2-coordinate segments.

        Returns:
            List of (start_coord, end_coord) tuples
        """
        segments = []
        for i in range(len(self.coordinates) - 1):
            start = self.coordinates[i]
            end = self.coordinates[i + 1]
            segments.append((start, end))
            logger.info(
                f"Segment {i}: ({start['lat']:.4f}, {start['lng']:.4f}) "
                f"-> ({end['lat']:.4f}, {end['lng']:.4f})"
            )
        return segments

    async def request_segment_alternatives(
        self,
        segment_index: int,
        start_coord: Dict[str, float],
        end_coord: Dict[str, float],
        request_osrm_fn,
        num_alternatives: int = 3,
    ) -> List[SegmentAlternative]:
        """
        Request alternatives from OSRM for a single segment.

        Args:
            segment_index: Index of this segment
            start_coord: Starting waypoint {"lat": ..., "lng": ...}
            end_coord: Ending waypoint
            request_osrm_fn: Async function to call OSRM (from api_routing)
            num_alternatives: Number of alternatives to request

        Returns:
            List of SegmentAlternative objects
        """
        try:
            coord_str = f"{start_coord['lng']},{start_coord['lat']};{end_coord['lng']},{end_coord['lat']}"

            params = {
                "alternatives": num_alternatives,
                "overview": "full",
                "geometries": "geojson",
            }

            logger.info(
                f"Requesting alternatives for segment {segment_index}: {coord_str}"
            )

            osrm_response = await request_osrm_fn(
                request_type="route",
                coordinates=coord_str,
                params=params,
            )

            if not osrm_response.get("routes"):
                logger.warning(f"No routes returned for segment {segment_index}")
                return []

            alternatives = []
            for route_idx, route in enumerate(osrm_response["routes"]):
                alt = SegmentAlternative(
                    segment_index=segment_index,
                    route_option=route_idx,
                    distance=route.get("distance", 0),
                    duration=route.get("duration", 0),
                    geometry=route.get("geometry", {}).get("coordinates", []),
                )
                alternatives.append(alt)
                logger.debug(
                    f"Segment {segment_index} option {route_idx}: "
                    f"{alt.distance:.0f}m, {alt.duration:.0f}s"
                )

            return alternatives

        except Exception as e:
            logger.error(
                f"Error requesting alternatives for segment {segment_index}: {e}"
            )
            return []

    async def get_all_segment_alternatives(
        self, request_osrm_fn, num_alternatives: int = 3
    ) -> bool:
        """
        Request alternatives for all segments in parallel.

        Args:
            request_osrm_fn: Async function to call OSRM
            num_alternatives: Number of alternatives per segment

        Returns:
            True if successful, False otherwise
        """
        segments = self.decompose_into_segments()

        logger.info(f"Requesting alternatives for {len(segments)} segments")

        # Request alternatives for all segments in parallel
        tasks = [
            self.request_segment_alternatives(
                i, start, end, request_osrm_fn, num_alternatives
            )
            for i, (start, end) in enumerate(segments)
        ]

        results = await asyncio.gather(*tasks)
        self.segment_alternatives = results

        return all(len(alts) > 0 for alts in results)

    def generate_complete_routes(self) -> List[Dict[str, Any]]:
        """
        Generate complete route alternatives by combining segment alternatives.

        Uses a greedy approach:
        1. First, try to use best option (route_option=0) for all segments
        2. Then, try variations with 2nd best options
        3. Score each complete route based on avoid zones

        Returns:
            List of complete route alternatives with scores
        """
        if not self.segment_alternatives:
            logger.warning("No segment alternatives available")
            return []

        # Check that each segment has at least one alternative
        for i, alts in enumerate(self.segment_alternatives):
            if not alts:
                logger.error(f"No alternatives for segment {i}")
                return []

        complete_routes = []
        max_options = max(len(alts) for alts in self.segment_alternatives)

        # Generate combinations: try progressively using more alternatives
        for option_level in range(max_options):
            # For each segment, use up to the current option level
            route_combinations = self._generate_option_combinations(option_level)

            for combo_idx, combination in enumerate(route_combinations):
                if complete_route := self._combine_segments(combination):
                    complete_route["route_index"] = len(complete_routes)
                    complete_route["option_level"] = option_level
                    complete_routes.append(complete_route)

                    logger.debug(
                        f"Route combination {len(complete_routes)}: "
                        f"{complete_route['distance']:.0f}m, "
                        f"{complete_route['duration']:.0f}s"
                    )

        # Score routes based on avoid zones if present
        if self.avoid_zones:
            self._score_routes_by_avoid_zones(complete_routes)
            # Sort by penalty score (best first)
            complete_routes.sort(key=lambda r: r.get("penalty_score", 0))

        return complete_routes

    def _generate_option_combinations(self, max_option: int) -> List[List[int]]:
        """
        Generate all combinations of segment options up to max_option.

        Returns:
            List of option combinations. Each combo is a list where
            combo[i] = which option (0, 1, 2...) to use for segment i
        """
        combinations = []

        def generate(segment_idx, current_combo):
            if segment_idx == len(self.segment_alternatives):
                combinations.append(current_combo[:])
                return

            # For this segment, try options up to max_option
            max_available = min(
                max_option, len(self.segment_alternatives[segment_idx]) - 1
            )
            for option in range(max_available + 1):
                current_combo.append(option)
                generate(segment_idx + 1, current_combo)
                current_combo.pop()

        generate(0, [])
        return combinations

    def _combine_segments(
        self, option_combination: List[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Combine selected alternatives from each segment into a complete route.

        Args:
            option_combination: List of option indices for each segment

        Returns:
            Complete route dict or None if invalid
        """
        if len(option_combination) != len(self.segment_alternatives):
            return None

        # Validate that each option index is available
        for seg_idx, opt_idx in enumerate(option_combination):
            if opt_idx >= len(self.segment_alternatives[seg_idx]):
                return None

        # Combine geometries
        combined_geometry = []
        total_distance = 0
        total_duration = 0

        for seg_idx, opt_idx in enumerate(option_combination):
            segment_alt = self.segment_alternatives[seg_idx][opt_idx]

            # Add geometry (avoid duplicating segment endpoints)
            if seg_idx == 0:
                # First segment: add all points
                combined_geometry.extend(segment_alt.geometry)
            else:
                # Subsequent segments: skip the first point (duplicate)
                combined_geometry.extend(segment_alt.geometry[1:])

            total_distance += segment_alt.distance
            total_duration += segment_alt.duration

        return {
            "geometry": {"coordinates": combined_geometry, "type": "LineString"},
            "distance": total_distance,
            "duration": total_duration,
            "option_combination": option_combination,
            "penalty_score": 0.0,  # Will be updated if avoid_zones present
        }

    def _score_routes_by_avoid_zones(self, routes: List[Dict]) -> None:
        """
        Score routes based on avoid zone intersections.

        Args:
            routes: List of complete routes to score
        """
        # Import here to avoid circular imports
        from webrotas.geojson_converter import avoid_zones_to_geojson
        from webrotas.api_routing import load_spatial_index, check_route_intersections

        try:
            geojson = avoid_zones_to_geojson(self.avoid_zones)
            polys, tree = load_spatial_index(geojson)

            if not polys:
                logger.debug("No valid polygons in avoid zones")
                return

            for route in routes:
                coords = route["geometry"]["coordinates"]
                intersection_data = check_route_intersections(coords, polys, tree)
                route["penalty_score"] = intersection_data["penalty_ratio"]
                route["zone_intersections"] = intersection_data["intersection_count"]

        except Exception as e:
            logger.error(f"Error scoring routes by avoid zones: {e}")


async def get_alternatives_for_multipoint_route(
    coordinates: List[Dict[str, float]],
    request_osrm_fn,
    avoid_zones: Optional[List] = None,
    num_alternatives: int = 3,
    max_routes: int = 6,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Get alternative routes for a multi-waypoint routing request.

    This is the main entry point for segment-based alternatives.

    Args:
        coordinates: List of waypoints with 'lat' and 'lng'
        request_osrm_fn: Async function to call OSRM API
        avoid_zones: Optional list of avoid zone definitions
        num_alternatives: Alternatives per segment
        max_routes: Maximum complete routes to return

    Returns:
        Tuple of (complete_routes_list, error_message)
        Returns ([], error_msg) if error occurs
    """
    logger.info(f"Building alternatives for {len(coordinates)} waypoints")

    if len(coordinates) < 2:
        return [], "Need at least 2 coordinates"

    # If only 2 coordinates, use standard OSRM alternatives
    if len(coordinates) == 2:
        logger.info("Only 2 coordinates - using standard OSRM alternatives")
        return [], "Use standard OSRM alternatives for 2-coordinate requests"

    # Multi-waypoint: use segment-based approach
    builder = SegmentAlternativesBuilder(coordinates, avoid_zones)

    try:
        # Request alternatives for all segments
        success = await builder.get_all_segment_alternatives(
            request_osrm_fn, num_alternatives
        )

        if not success:
            return [], "Failed to get alternatives for all segments"

        # Generate complete route combinations
        complete_routes = builder.generate_complete_routes()

        # Limit to max_routes
        if len(complete_routes) > max_routes:
            complete_routes = complete_routes[:max_routes]

        logger.info(
            f"Generated {len(complete_routes)} alternative complete routes "
            f"from {builder.num_segments} segments"
        )

        return complete_routes, None

    except Exception as e:
        logger.error(f"Error generating alternatives: {e}", exc_info=True)
        return [], f"Error: {str(e)}"

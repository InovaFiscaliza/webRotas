"""
Iterative Distance/Duration Matrix Builder

Constructs complete distance and duration matrices by making sequential
requests to the public OSRM API, respecting rate limits and API constraints.

When the local container is unavailable, this module allows building matrices
for any number of coordinates by iteratively requesting batches.
"""

import time
from typing import List, Tuple, Dict
from dataclasses import dataclass

import requests
from geopy.distance import geodesic

from webrotas.config.logging_config import get_logger

logger = get_logger(__name__)

# Configuration constants
PUBLIC_API_BATCH_SIZE = 95  # Conservative: 95 waypoints + 1 origin
PUBLIC_API_MAX_RETRIES = 3
PUBLIC_API_RETRY_BASE_DELAY = 1.0  # seconds
PUBLIC_API_RATE_LIMIT_DELAY = 0.5  # seconds between requests
TIMEOUT = 10

URL_TABLE = "http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration"


@dataclass
class RequestBatch:
    """Represents a single batch of coordinates for API request."""

    origin_idx: int
    waypoint_indices: List[int]
    coords: List[Dict]

    @property
    def size(self) -> int:
        """Total coordinates in this batch (origin + waypoints)."""
        return 1 + len(self.waypoint_indices)

    def to_coord_string(self) -> str:
        """Format coordinates as OSRM URL parameter."""
        batch_coords = [self.coords[self.origin_idx]] + [
            self.coords[i] for i in self.waypoint_indices
        ]
        return ";".join(f"{c['lng']},{c['lat']}" for c in batch_coords)


class IterativeMatrixBuilder:
    """
    Builds distance and duration matrices by iteratively requesting batches
    from the public OSRM API.

    The algorithm splits coordinates into batches respecting the 100-waypoint
    public API limit and makes sequential requests with rate limiting and
    automatic fallback to geodesic calculation on failures.
    """

    def __init__(
        self,
        coords: List[Dict],
        batch_size: int = PUBLIC_API_BATCH_SIZE,
        max_retries: int = PUBLIC_API_MAX_RETRIES,
        retry_delay: float = PUBLIC_API_RETRY_BASE_DELAY,
        rate_limit_delay: float = PUBLIC_API_RATE_LIMIT_DELAY,
    ):
        """
        Initialize the matrix builder.

        Args:
            coords: List of coordinate dicts with 'lat' and 'lng' keys
            batch_size: Max waypoints per request (default: 95)
            max_retries: Max retry attempts per request
            retry_delay: Base delay for exponential backoff (seconds)
            rate_limit_delay: Delay between requests (seconds)
        """
        self.coords = coords
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.num_coords = len(coords)

        # Initialize matrices with zeros
        self.distances = [[0.0] * self.num_coords for _ in range(self.num_coords)]
        self.durations = [[0.0] * self.num_coords for _ in range(self.num_coords)]

        # Track failed pairs for fallback
        self.failed_pairs: List[Tuple[int, int]] = []

    def build(self) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Build the complete distance and duration matrices.

        Returns:
            Tuple of (distances, durations) matrices

        Raises:
            ValueError: If matrix building fails completely
        """
        logger.info(
            f"Starting iterative matrix build for {self.num_coords} coordinates "
            f"with batch size {self.batch_size}"
        )

        batches = self._create_batches()
        logger.info(f"Created {len(batches)} batches for API requests")

        for batch_idx, batch in enumerate(batches):
            logger.debug(
                f"Processing batch {batch_idx + 1}/{len(batches)} "
                f"(origin {batch.origin_idx}, waypoints {len(batch.waypoint_indices)})"
            )

            success = self._process_batch(batch)

            if not success:
                logger.warning(
                    f"Batch {batch_idx + 1} failed after retries, "
                    f"will use geodesic fallback for failed pairs"
                )

            # Rate limiting between requests
            if batch_idx < len(batches) - 1:
                time.sleep(self.rate_limit_delay)

        # Apply geodesic fallback for any failed pairs
        if self.failed_pairs:
            logger.info(
                f"Applying geodesic fallback for {len(self.failed_pairs)} failed pairs"
            )
            self._apply_geodesic_fallback()

        logger.info("Matrix build completed successfully")
        return self.distances, self.durations

    def _create_batches(self) -> List[RequestBatch]:
        """
        Create batches respecting the maximum batch size.

        Each batch uses coordinate 0 (origin) as the reference point and
        includes up to batch_size waypoints.

        Returns:
            List of RequestBatch objects
        """
        batches = []

        # First batch: origin + waypoints
        for start_idx in range(1, self.num_coords, self.batch_size):
            end_idx = min(start_idx + self.batch_size, self.num_coords)
            waypoint_indices = list(range(start_idx, end_idx))

            batch = RequestBatch(
                origin_idx=0, waypoint_indices=waypoint_indices, coords=self.coords
            )
            batches.append(batch)

        # Additional batches: each waypoint as origin with remaining waypoints
        for origin_idx in range(1, self.num_coords):
            # Get waypoints that haven't been paired with this origin yet
            waypoint_indices = []

            for waypoint_idx in range(origin_idx + 1, self.num_coords):
                waypoint_indices.append(waypoint_idx)

                if len(waypoint_indices) >= self.batch_size:
                    batch = RequestBatch(
                        origin_idx=origin_idx,
                        waypoint_indices=waypoint_indices[:],
                        coords=self.coords,
                    )
                    batches.append(batch)
                    waypoint_indices = []

            # Add remaining waypoints
            if waypoint_indices:
                batch = RequestBatch(
                    origin_idx=origin_idx,
                    waypoint_indices=waypoint_indices,
                    coords=self.coords,
                )
                batches.append(batch)

        return batches

    def _process_batch(self, batch: RequestBatch) -> bool:
        """
        Process a single batch with retries.

        Args:
            batch: The RequestBatch to process

        Returns:
            True if successful, False if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self._request_batch(batch)
                self._merge_batch_response(batch, response)
                return True

            except requests.exceptions.RequestException as e:
                delay = self.retry_delay * (2**attempt)
                logger.warning(
                    f"Batch request attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                if attempt < self.max_retries - 1:
                    time.sleep(delay)

            except (ValueError, KeyError) as e:
                logger.error(f"Invalid response format in batch: {e}")
                return False

        # All retries exhausted
        self._mark_batch_failed(batch)
        return False

    def _request_batch(self, batch: RequestBatch) -> Dict:
        """
        Request matrix for a batch from public API.

        Args:
            batch: The RequestBatch to request

        Returns:
            Response JSON from API

        Raises:
            requests.exceptions.RequestException: On HTTP errors
            ValueError: On invalid response format
        """
        coord_str = batch.to_coord_string()
        url = URL_TABLE.format(coord_str=coord_str)

        logger.debug(f"Requesting batch from {url[:80]}...")

        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()

        data = response.json()

        if "distances" not in data or "durations" not in data:
            raise ValueError("Missing distances or durations in response")

        return data

    def _merge_batch_response(self, batch: RequestBatch, response: Dict) -> None:
        """
        Merge batch response into the main matrices.

        Args:
            batch: The RequestBatch that was requested
            response: The API response JSON
        """
        distances = response["distances"]
        durations = response["durations"]

        # First row is origin → waypoints
        origin_idx = batch.origin_idx
        for local_idx, waypoint_idx in enumerate(batch.waypoint_indices):
            self.distances[origin_idx][waypoint_idx] = distances[0][local_idx + 1]
            self.durations[origin_idx][waypoint_idx] = durations[0][local_idx + 1]

        # Remaining rows are waypoint → waypoints (if needed)
        for local_origin_idx, waypoint_origin_idx in enumerate(batch.waypoint_indices):
            for local_dest_idx, waypoint_dest_idx in enumerate(batch.waypoint_indices):
                if waypoint_origin_idx != waypoint_dest_idx:
                    self.distances[waypoint_origin_idx][waypoint_dest_idx] = distances[
                        local_origin_idx + 1
                    ][local_dest_idx + 1]
                    self.durations[waypoint_origin_idx][waypoint_dest_idx] = durations[
                        local_origin_idx + 1
                    ][local_dest_idx + 1]

    def _mark_batch_failed(self, batch: RequestBatch) -> None:
        """
        Mark all pairs in a batch as failed for geodesic fallback.

        Args:
            batch: The failed RequestBatch
        """
        origin_idx = batch.origin_idx
        for waypoint_idx in batch.waypoint_indices:
            self.failed_pairs.append((origin_idx, waypoint_idx))
            self.failed_pairs.append((waypoint_idx, origin_idx))

    def _apply_geodesic_fallback(self, speed_kmh: float = 40) -> None:
        """
        Apply geodesic calculation for failed pairs.

        Args:
            speed_kmh: Speed in km/h for duration calculation
        """
        for i, j in self.failed_pairs:
            if i != j:
                p1 = (self.coords[i]["lat"], self.coords[i]["lng"])
                p2 = (self.coords[j]["lat"], self.coords[j]["lng"])
                distance_m = geodesic(p1, p2).meters
                self.distances[i][j] = distance_m
                self.durations[i][j] = (distance_m / speed_kmh) * 3.6

                logger.debug(
                    f"Geodesic fallback: pair ({i}, {j}) = {distance_m:.1f}m, "
                    f"{self.durations[i][j]:.1f}s"
                )

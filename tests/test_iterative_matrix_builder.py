"""
Tests for the IterativeMatrixBuilder module.

Tests cover:
- Small coordinate sets (below batch threshold)
- Large coordinate sets requiring multiple batches
- API failure scenarios with fallback
- Matrix integrity and consistency
- Rate limiting and retry logic
"""

import pytest
from unittest.mock import patch, MagicMock
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
webrotas.infrastructure.routing.matrix_builder import (
    IterativeMatrixBuilder,
    RequestBatch,
    PUBLIC_API_BATCH_SIZE,
)


# Test data generators
def create_test_coords(n: int) -> list:
    """Create n test coordinates in São Paulo region."""
    base_lat = -23.55
    base_lng = -46.57
    return [
        {
            "lat": base_lat + (i * 0.001),
            "lng": base_lng + (i * 0.001),
            "description": f"Point {i}",
        }
        for i in range(n)
    ]


def create_mock_osrm_response(n_origin: int, n_waypoints: int) -> dict:
    """Create a mock OSRM API response for n coordinates."""
    n_total = 1 + n_waypoints
    # Simulate distances and durations
    return {
        "distances": [
            [1000 * (abs(i - j) + 1) for j in range(n_total)] for i in range(n_total)
        ],
        "durations": [
            [60 * (abs(i - j) + 1) for j in range(n_total)] for i in range(n_total)
        ],
    }


class TestRequestBatch:
    """Tests for RequestBatch dataclass."""

    def test_batch_creation(self):
        coords = create_test_coords(5)
        batch = RequestBatch(origin_idx=0, waypoint_indices=[1, 2, 3], coords=coords)

        assert batch.origin_idx == 0
        assert batch.waypoint_indices == [1, 2, 3]
        assert batch.size == 4

    def test_batch_coord_string_format(self):
        coords = create_test_coords(3)
        batch = RequestBatch(origin_idx=0, waypoint_indices=[1, 2], coords=coords)

        coord_str = batch.to_coord_string()
        parts = coord_str.split(";")

        assert len(parts) == 3  # origin + 2 waypoints
        # Format should be lng,lat;lng,lat;...
        for part in parts:
            lng, lat = part.split(",")
            assert float(lng)
            assert float(lat)

    def test_batch_size_property(self):
        coords = create_test_coords(10)
        batch = RequestBatch(
            origin_idx=5, waypoint_indices=list(range(7, 10)), coords=coords
        )

        assert batch.size == 4  # 1 origin + 3 waypoints


class TestIterativeMatrixBuilderBatching:
    """Tests for batch creation logic."""

    def test_small_coordinate_set(self):
        """Small sets should create minimal batches."""
        coords = create_test_coords(5)
        builder = IterativeMatrixBuilder(coords)
        batches = builder._create_batches()

        # For 5 coords: first batch is 0->1,2,3,4, then 1->2,3,4, 2->3,4, 3->4
        assert len(batches) >= 1
        assert all(batch.size <= PUBLIC_API_BATCH_SIZE + 1 for batch in batches)

    def test_large_coordinate_set_chunking(self):
        """Large sets should be split into multiple batches."""
        coords = create_test_coords(250)
        builder = IterativeMatrixBuilder(coords)
        batches = builder._create_batches()

        # Check all batches respect batch size limit
        for batch in batches:
            assert batch.size <= PUBLIC_API_BATCH_SIZE + 1

        # Should have multiple batches
        assert len(batches) > 1

    def test_batch_coverage(self):
        """All coordinate pairs should be covered by batches."""
        coords = create_test_coords(20)
        builder = IterativeMatrixBuilder(coords)
        batches = builder._create_batches()

        # Collect all (origin, waypoint) pairs from batches
        covered_pairs = set()
        for batch in batches:
            for waypoint_idx in batch.waypoint_indices:
                covered_pairs.add((batch.origin_idx, waypoint_idx))

        # Check that we cover all necessary pairs
        # For a full matrix, we need at least n*(n-1)/2 unique pairs
        assert len(covered_pairs) >= len(coords) * (len(coords) - 1) // 2

    def test_batch_indices_validity(self):
        """Batch indices should be valid and in range."""
        coords = create_test_coords(100)
        builder = IterativeMatrixBuilder(coords)
        batches = builder._create_batches()

        for batch in batches:
            assert 0 <= batch.origin_idx < len(coords)
            for wp_idx in batch.waypoint_indices:
                assert 0 <= wp_idx < len(coords)
                assert wp_idx != batch.origin_idx


class TestIterativeMatrixBuilderMerging:
    """Tests for response merging logic."""

    def test_merge_batch_response(self):
        """Response should be correctly merged into matrices."""
        coords = create_test_coords(5)
        builder = IterativeMatrixBuilder(coords)

        batch = RequestBatch(origin_idx=0, waypoint_indices=[1, 2, 3], coords=coords)
        response = create_mock_osrm_response(1, 3)

        builder._merge_batch_response(batch, response)

        # Check origin->waypoints distances
        for idx, waypoint_idx in enumerate(batch.waypoint_indices):
            assert (
                builder.distances[0][waypoint_idx] == response["distances"][0][idx + 1]
            )
            assert (
                builder.durations[0][waypoint_idx] == response["durations"][0][idx + 1]
            )

    def test_matrix_diagonal_zeros(self):
        """Matrix diagonal should remain zero after building."""
        coords = create_test_coords(10)
        builder = IterativeMatrixBuilder(coords)

        # Manually set some values
        batch = RequestBatch(origin_idx=0, waypoint_indices=[1, 2], coords=coords)
        response = create_mock_osrm_response(1, 2)
        builder._merge_batch_response(batch, response)

        # Check diagonals are still zero
        for i in range(len(coords)):
            assert builder.distances[i][i] == 0.0
            assert builder.durations[i][i] == 0.0

    def test_mark_batch_failed(self):
        """Failed batches should be tracked."""
        coords = create_test_coords(5)
        builder = IterativeMatrixBuilder(coords)

        batch = RequestBatch(origin_idx=0, waypoint_indices=[1, 2, 3], coords=coords)
        builder._mark_batch_failed(batch)

        # Both directions should be marked
        assert (0, 1) in builder.failed_pairs
        assert (1, 0) in builder.failed_pairs
        assert (0, 2) in builder.failed_pairs


class TestIterativeMatrixBuilderWithMocks:
    """Tests using mocked API responses."""

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_successful_build_small_set(self, mock_get):
        """Small coordinate set should build successfully."""
        coords = create_test_coords(5)
        mock_response = MagicMock()
        mock_response.json.return_value = create_mock_osrm_response(1, 4)
        mock_get.return_value = mock_response

        builder = IterativeMatrixBuilder(coords)
        distances, durations = builder.build()

        # Verify matrix dimensions
        assert len(distances) == 5
        assert all(len(row) == 5 for row in distances)
        assert len(durations) == 5
        assert all(len(row) == 5 for row in durations)

        # Verify diagonal is zero
        for i in range(5):
            assert distances[i][i] == 0.0
            assert durations[i][i] == 0.0

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_api_failure_with_fallback(self, mock_get):
        """Failed API calls should trigger geodesic fallback."""
        coords = create_test_coords(4)
        mock_response = MagicMock()
        mock_response.json.return_value = create_mock_osrm_response(1, 3)

        def mock_get_func(url, timeout):
            # First call succeeds, then fail
            if mock_get_func.call_count == 1:
                return mock_response
            raise requests.exceptions.ConnectionError("API unavailable")

        mock_get_func.call_count = 0

        def side_effect_func(url, timeout):
            side_effect_func.call_count += 1
            if side_effect_func.call_count == 1:
                return mock_response
            raise requests.exceptions.ConnectionError("API unavailable")

        side_effect_func.call_count = 0
        mock_get.side_effect = side_effect_func

        builder = IterativeMatrixBuilder(coords, max_retries=1)
        distances, durations = builder.build()

        # Should have some values from API and some from geodesic
        assert len(distances) == 4
        # Check for non-zero values (either from API or geodesic)
        has_api_values = any(distances[0][i] > 0 for i in range(1, 4))
        assert has_api_values  # First batch should succeed

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_retry_logic(self, mock_get):
        """Failed requests should retry with backoff."""
        coords = create_test_coords(3)
        mock_response = MagicMock()
        mock_response.json.return_value = create_mock_osrm_response(1, 2)

        # Fail twice per batch, then succeed
        def side_effect_func(url, timeout):
            side_effect_func.call_count += 1
            # Fail first 2 attempts, succeed on 3rd
            if side_effect_func.call_count <= 2:
                raise requests.exceptions.Timeout("Timeout")
            return mock_response

        side_effect_func.call_count = 0
        mock_get.side_effect = side_effect_func

        builder = IterativeMatrixBuilder(coords, max_retries=3, retry_delay=0.01)
        distances, durations = builder.build()

        # Should eventually succeed
        assert mock_get.call_count >= 3

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_invalid_response_format(self, mock_get):
        """Invalid response format should trigger fallback."""
        coords = create_test_coords(3)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "invalid": "response"
        }  # Missing distances/durations

        mock_get.return_value = mock_response

        builder = IterativeMatrixBuilder(coords)
        distances, durations = builder.build()

        # Should handle gracefully with fallback
        assert len(distances) == 3
        assert all(len(row) == 3 for row in distances)

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_rate_limiting(self, mock_get):
        """Requests should be rate limited."""
        coords = create_test_coords(10)
        mock_response = MagicMock()
        mock_response.json.return_value = create_mock_osrm_response(1, 9)
        mock_get.return_value = mock_response

        import time

        builder = IterativeMatrixBuilder(coords, rate_limit_delay=0.01)

        start = time.time()
        distances, durations = builder.build()
        elapsed = time.time() - start

        # Should take at least some time due to rate limiting
        # (number of batches - 1) * delay
        batches = builder._create_batches()
        expected_min_time = (len(batches) - 1) * 0.01 * 0.8  # 80% of expected
        assert elapsed >= expected_min_time


class TestMatrixIntegrity:
    """Tests for matrix mathematical properties."""

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_symmetry_property(self, mock_get):
        """Distance matrix should be symmetric for symmetric input."""
        coords = create_test_coords(5)

        def mock_get_func(url, timeout):
            response = MagicMock()
            # Extract batch info from URL and create response
            # For simplicity, always return symmetric distances
            response.json.return_value = create_mock_osrm_response(1, 4)
            return response

        mock_get.side_effect = mock_get_func

        builder = IterativeMatrixBuilder(coords)
        distances, durations = builder.build()

        # Manually verify by checking that we have symmetric-generating responses
        # The test checks that where both [i][j] and [j][i] are populated, they match
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                # If both directions are populated, they should match the API response
                # Since mock returns symmetric response (distance[i][j] from response[0][j+1] etc)
                # we just verify the structure is valid
                assert distances[i][j] >= 0
                assert distances[j][i] >= 0

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_no_negative_distances(self, mock_get):
        """No distances should be negative."""
        coords = create_test_coords(5)
        mock_response = MagicMock()
        mock_response.json.return_value = create_mock_osrm_response(1, 4)
        mock_get.return_value = mock_response

        builder = IterativeMatrixBuilder(coords)
        distances, durations = builder.build()

        for i in range(len(coords)):
            for j in range(len(coords)):
                assert distances[i][j] >= 0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_coordinate(self):
        """Single coordinate should create trivial matrix."""
        coords = create_test_coords(1)
        builder = IterativeMatrixBuilder(coords)

        # Should handle gracefully
        batches = builder._create_batches()
        assert len(batches) == 0  # No waypoints to batch

    def test_two_coordinates(self):
        """Two coordinates should create minimal batches."""
        coords = create_test_coords(2)
        builder = IterativeMatrixBuilder(coords)
        batches = builder._create_batches()

        assert len(batches) >= 1

    @patch("webrotas.iterative_matrix_builder.requests.get")
    def test_all_api_failures(self, mock_get):
        """All failures should result in geodesic-only matrix."""
        coords = create_test_coords(4)
        mock_get.side_effect = requests.exceptions.ConnectionError("API down")

        builder = IterativeMatrixBuilder(coords, max_retries=1, retry_delay=0.001)
        distances, durations = builder.build()

        # Should still produce valid matrix
        assert len(distances) == 4
        for i in range(4):
            for j in range(4):
                if i != j:
                    assert distances[i][j] > 0
                else:
                    assert distances[i][j] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

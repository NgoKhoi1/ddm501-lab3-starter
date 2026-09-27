"""
Unit tests for Pydantic schemas.

TODO: Complete the test implementations below.

Run tests:
    pytest tests/unit/test_schemas.py -v
"""

import pytest
from pydantic import ValidationError

from app.schemas import (
    BatchPredictionRequest,
    HealthResponse,
    PredictionItem,
    PredictionRequest,
    PredictionResponse,
)


class TestPredictionRequest:
    """Tests for PredictionRequest schema."""

    # =========================================================================
    # Valid Input Tests (PROVIDED)
    # =========================================================================

    def test_valid_request(self):
        """Test that valid request passes validation."""
        request = PredictionRequest(user_id="196", movie_id="242")
        assert request.user_id == "196"
        assert request.movie_id == "242"

    def test_valid_request_with_numeric_strings(self):
        """Test numeric string IDs are valid."""
        request = PredictionRequest(user_id="123", movie_id="456")
        assert request.user_id == "123"
        assert request.movie_id == "456"

    # =========================================================================
    # TODO 1: Implement Missing Field Tests
    # =========================================================================

    def test_missing_user_id_raises_error(self):
        """
        Test that missing user_id raises ValidationError.

        TODO: Implement this test
        - Use pytest.raises(ValidationError)
        - Try to create PredictionRequest without user_id
        """
        with pytest.raises(ValidationError):
            PredictionRequest(movie_id="242")

    def test_missing_movie_id_raises_error(self):
        """
        Test that missing movie_id raises ValidationError.

        TODO: Implement this test
        """
        with pytest.raises(ValidationError):
            PredictionRequest(user_id="196")

    def test_missing_both_fields_raises_error(self):
        """
        Test that missing both fields raises ValidationError.

        TODO: Implement this test
        """
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest()
        # Both fields should be reported
        assert exc_info.value.error_count() == 2

    # =========================================================================
    # TODO 2: Implement Empty/Invalid Input Tests
    # =========================================================================

    def test_empty_user_id_raises_error(self):
        """
        Test that empty user_id raises ValidationError.

        TODO: Implement this test
        """
        with pytest.raises(ValidationError):
            PredictionRequest(user_id="", movie_id="242")

    def test_whitespace_only_user_id_raises_error(self):
        """
        Test that whitespace-only user_id raises ValidationError.

        TODO: Implement this test
        """
        with pytest.raises(ValidationError):
            PredictionRequest(user_id="   ", movie_id="242")

    def test_none_values_raise_error(self):
        """
        Test that None values raise ValidationError.

        TODO: Implement this test
        """
        with pytest.raises(ValidationError):
            PredictionRequest(user_id=None, movie_id="242")
        with pytest.raises(ValidationError):
            PredictionRequest(user_id="196", movie_id=None)

    # =========================================================================
    # TODO 3: Implement Type Validation Tests
    # =========================================================================

    def test_integer_user_id_converted_to_string(self):
        """
        Test how integer user_id is handled.

        TODO: Implement this test
        - Pydantic may convert int to string or raise error
        - Test the actual behavior
        """
        # Pydantic v2 does not coerce int to str, so an int ID is rejected
        with pytest.raises(ValidationError):
            PredictionRequest(user_id=196, movie_id="242")


class TestPredictionResponse:
    """Tests for PredictionResponse schema."""

    # =========================================================================
    # TODO 4: Implement Response Validation Tests
    # =========================================================================

    def test_valid_response(self):
        """
        Test that valid response passes validation.

        TODO: Implement this test
        """
        response = PredictionResponse(
            user_id="196", movie_id="242", predicted_rating=3.5, model_version="1.0.0"
        )
        assert response.predicted_rating == 3.5
        assert response.model_version == "1.0.0"

    def test_rating_below_minimum_raises_error(self):
        """
        Test that rating below 1.0 raises ValidationError.

        TODO: Implement this test
        """
        with pytest.raises(ValidationError):
            PredictionResponse(
                user_id="196",
                movie_id="242",
                predicted_rating=0.5,  # Below minimum
                model_version="1.0.0",
            )

    def test_rating_above_maximum_raises_error(self):
        """
        Test that rating above 5.0 raises ValidationError.

        TODO: Implement this test
        """
        with pytest.raises(ValidationError):
            PredictionResponse(
                user_id="196",
                movie_id="242",
                predicted_rating=5.5,  # Above maximum
                model_version="1.0.0",
            )

    def test_rating_at_boundaries(self):
        """
        Test ratings at exact boundaries (1.0 and 5.0).

        TODO: Implement this test
        """
        for rating in (1.0, 5.0):
            response = PredictionResponse(
                user_id="196", movie_id="242", predicted_rating=rating, model_version="1.0.0"
            )
            assert response.predicted_rating == rating


class TestHealthResponse:
    """Tests for HealthResponse schema."""

    # =========================================================================
    # TODO 5: Implement Health Response Tests
    # =========================================================================

    def test_valid_health_response(self):
        """
        Test that valid health response passes validation.

        TODO: Implement this test
        """
        response = HealthResponse(status="healthy", model_loaded=True)
        assert response.status == "healthy"
        assert response.model_loaded is True

    def test_health_response_status_types(self):
        """
        Test various status values.

        TODO: Implement this test
        """
        for status, loaded in (("healthy", True), ("unhealthy", False)):
            response = HealthResponse(status=status, model_loaded=loaded)
            assert response.status == status
            assert response.model_loaded is loaded

        # status must be a string
        with pytest.raises(ValidationError):
            HealthResponse(status=None, model_loaded=True)


class TestBatchPredictionRequest:
    """Tests for BatchPredictionRequest schema."""

    # =========================================================================
    # TODO 6: Implement Batch Request Tests (BONUS)
    # =========================================================================

    def test_valid_batch_request(self):
        """
        Test that valid batch request passes validation.

        TODO: Implement this test (BONUS)
        """
        request = BatchPredictionRequest(
            predictions=[
                PredictionItem(user_id="196", movie_id="242"),
                {"user_id": "186", "movie_id": "302"},
            ]
        )
        assert len(request.predictions) == 2
        assert all(isinstance(p, PredictionItem) for p in request.predictions)

    def test_empty_predictions_list_raises_error(self):
        """
        Test that empty predictions list raises ValidationError.

        TODO: Implement this test (BONUS)
        """
        with pytest.raises(ValidationError):
            BatchPredictionRequest(predictions=[])

    def test_too_many_predictions_raises_error(self):
        """
        Test that too many predictions raises ValidationError.

        TODO: Implement this test (BONUS)
        - The schema has max_length=100
        """
        items = [{"user_id": "196", "movie_id": "242"}] * 101
        with pytest.raises(ValidationError):
            BatchPredictionRequest(predictions=items)

        # Exactly 100 is still allowed
        request = BatchPredictionRequest(predictions=items[:100])
        assert len(request.predictions) == 100


# =============================================================================
# Run tests
# =============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

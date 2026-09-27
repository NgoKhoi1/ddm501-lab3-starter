"""
Data quality validation tests.

TODO: Complete the test implementations below.

Run tests:
    pytest tests/data/test_data_quality.py -v
"""

import numpy as np
import pytest


class TestRatingDataQuality:
    """Tests for rating data quality."""

    # =========================================================================
    # TODO 1: Implement Rating Range Tests
    # =========================================================================

    def test_all_ratings_in_valid_range(self, sample_ratings):
        """
        Test that all ratings are between 1.0 and 5.0.

        TODO: Implement this test
        - Loop through sample_ratings
        - Assert each rating is >= 1.0 and <= 5.0
        """
        for record in sample_ratings:
            assert 1.0 <= record["rating"] <= 5.0

    def test_no_negative_ratings(self, sample_ratings):
        """
        Test that there are no negative ratings.

        TODO: Implement this test
        """
        for record in sample_ratings:
            assert record["rating"] >= 0

    def test_no_ratings_above_maximum(self, sample_ratings):
        """
        Test that no ratings exceed 5.0.

        TODO: Implement this test
        """
        for record in sample_ratings:
            assert record["rating"] <= 5.0

    # =========================================================================
    # TODO 2: Implement ID Validation Tests
    # =========================================================================

    def test_no_missing_user_ids(self, sample_ratings):
        """
        Test that no user_ids are missing (None or empty).

        TODO: Implement this test
        """
        for record in sample_ratings:
            assert record["user_id"] is not None
            assert record["user_id"] != ""

    def test_no_missing_movie_ids(self, sample_ratings):
        """
        Test that no movie_ids are missing.

        TODO: Implement this test
        """
        for record in sample_ratings:
            assert record["movie_id"] is not None
            assert record["movie_id"] != ""

    def test_user_ids_are_strings(self, sample_ratings):
        """
        Test that all user_ids are strings.

        TODO: Implement this test
        """
        for record in sample_ratings:
            assert isinstance(record["user_id"], str)

    def test_movie_ids_are_strings(self, sample_ratings):
        """
        Test that all movie_ids are strings.

        TODO: Implement this test
        """
        for record in sample_ratings:
            assert isinstance(record["movie_id"], str)

    # =========================================================================
    # TODO 3: Implement Data Completeness Tests
    # =========================================================================

    def test_no_null_ratings(self, sample_ratings):
        """
        Test that no ratings are None/null.

        TODO: Implement this test
        """
        for record in sample_ratings:
            assert record["rating"] is not None
            assert not np.isnan(record["rating"])

    def test_all_records_have_required_fields(self, sample_ratings):
        """
        Test that all records have user_id, movie_id, and rating.

        TODO: Implement this test
        """
        required_fields = ["user_id", "movie_id", "rating"]
        for record in sample_ratings:
            for field in required_fields:
                assert field in record


class TestRatingDistribution:
    """Tests for rating distribution statistics."""

    # =========================================================================
    # TODO 4: Implement Distribution Tests
    # =========================================================================

    def test_mean_rating_reasonable(self, sample_ratings):
        """
        Test that mean rating is within reasonable range (2.0 - 4.5).

        TODO: Implement this test
        """
        ratings = [r["rating"] for r in sample_ratings]
        mean_rating = np.mean(ratings)
        assert 2.0 <= mean_rating <= 4.5

    def test_rating_standard_deviation(self, sample_ratings):
        """
        Test that rating standard deviation is reasonable.

        TODO: Implement this test
        - STD should be > 0 (some variation)
        - STD should be < 2.0 (not too much variation)
        """
        ratings = [r["rating"] for r in sample_ratings]
        std_rating = np.std(ratings)
        assert 0 < std_rating < 2.0

    def test_multiple_rating_values_exist(self, sample_ratings):
        """
        Test that there are multiple distinct rating values.

        TODO: Implement this test
        """
        ratings = [r["rating"] for r in sample_ratings]
        unique_ratings = set(ratings)
        assert len(unique_ratings) > 1


class TestDataUniqueness:
    """Tests for data uniqueness constraints."""

    # =========================================================================
    # TODO 5: Implement Uniqueness Tests
    # =========================================================================

    def test_unique_user_movie_combinations(self, sample_ratings):
        """
        Test that each (user_id, movie_id) pair is unique.

        TODO: Implement this test
        """
        pairs = [(r["user_id"], r["movie_id"]) for r in sample_ratings]
        assert len(pairs) == len(set(pairs))

    def test_multiple_users_exist(self, sample_ratings):
        """
        Test that there are multiple users in the dataset.

        TODO: Implement this test
        """
        users = {r["user_id"] for r in sample_ratings}
        assert len(users) > 1

    def test_multiple_movies_exist(self, sample_ratings):
        """
        Test that there are multiple movies in the dataset.

        TODO: Implement this test
        """
        movies = {r["movie_id"] for r in sample_ratings}
        assert len(movies) > 1


class TestDataTypes:
    """Tests for correct data types."""

    # =========================================================================
    # TODO 6: Implement Type Tests (BONUS)
    # =========================================================================

    def test_ratings_are_numeric(self, sample_ratings):
        """
        Test that all ratings are numeric (int or float).

        TODO: Implement this test (BONUS)
        """
        for record in sample_ratings:
            # bool is a subclass of int, so exclude it explicitly
            assert isinstance(record["rating"], (int, float))
            assert not isinstance(record["rating"], bool)

    def test_ratings_are_float_or_int(self, sample_ratings):
        """
        Test that ratings are float or can be converted to float.

        TODO: Implement this test (BONUS)
        """
        for record in sample_ratings:
            converted = float(record["rating"])
            assert converted == record["rating"]


# =============================================================================
# Run tests
# =============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
# tests/test_analyze.py - Test data analysis functionality
# Created: 2023-07-01
# Author: Developer

import unittest

# Import the function to test
from app import analyze


class TestAnalyze(unittest.TestCase):
    """Test cases for data analysis functionality."""

    def test_analyze_empty_data(self):
        """Test analyze function with empty data."""
        result = analyze([])

        # Check structure of result
        self.assertIn("top_routes", result)
        self.assertIn("price_trends", result)
        self.assertIn("summary", result)

        # Check empty results
        self.assertEqual(len(result["top_routes"]), 0)
        self.assertEqual(len(result["price_trends"]), 0)
        self.assertEqual(result["summary"]["total_routes"], 0)

    def test_analyze_sample_data(self):
        """Test analyze function with sample data."""
        # Sample data
        sample_data = [
            {
                "origin": "JFK",
                "destination": "LAX",
                "depart_date": "2023-07-15",
                "return_date": "2023-07-22",
                "price": 350,
                "airline": "AA",
                "flight_number": "AA123",
            },
            {
                "origin": "JFK",
                "destination": "LAX",
                "depart_date": "2023-07-16",
                "return_date": "2023-07-23",
                "price": 380,
                "airline": "AA",
                "flight_number": "AA123",
            },
            {
                "origin": "JFK",
                "destination": "SFO",
                "depart_date": "2023-07-15",
                "return_date": "2023-07-22",
                "price": 420,
                "airline": "UA",
                "flight_number": "UA456",
            },
        ]

        result = analyze(sample_data)

        # Check structure of result
        self.assertIn("top_routes", result)
        self.assertIn("price_trends", result)
        self.assertIn("summary", result)

        # Check top routes
        self.assertEqual(len(result["top_routes"]), 2)  # JFK-LAX and JFK-SFO

        # Find JFK-LAX route
        jfk_lax = next(
            (r for r in result["top_routes"] if r["destination"] == "LAX"), None
        )
        self.assertIsNotNone(jfk_lax)
        self.assertEqual(jfk_lax["count"], 2)

        # Check price trends
        self.assertEqual(len(result["price_trends"]), 2)  # Two unique dates

        # Check summary
        self.assertEqual(result["summary"]["total_routes"], 3)
        self.assertEqual(result["summary"]["min_price"], 350)
        self.assertEqual(result["summary"]["max_price"], 420)
        self.assertAlmostEqual(result["summary"]["avg_price"], 383.33, places=2)


if __name__ == "__main__":
    unittest.main()

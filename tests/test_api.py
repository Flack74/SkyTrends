#!/usr/bin/env python3
# tests/test_api.py - Test API functionality
# Created: 2023-07-01
# Author: Developer

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import fetch_api_data


class TestAPI(unittest.TestCase):
    """Test cases for API functionality."""

    @patch("app.requests.get")
    def test_fetch_api_data_success(self, mock_get):
        """Test successful API data fetch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "origin": "JFK",
                    "destination": "LAX",
                    "depart_date": "2023-07-15",
                    "return_date": "2023-07-22",
                    "price": 350,
                    "airline": "AA",
                    "flight_number": "AA123",
                }
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call function
        result = fetch_api_data("JFK", "LAX", "2023-07-15", "2023-07-22")

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["origin"], "JFK")
        self.assertEqual(result[0]["destination"], "LAX")
        self.assertEqual(result[0]["price"], 350)

        # Verify API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("api.travelpayouts.com", args[0])
        self.assertEqual(kwargs["params"]["origin"], "JFK")
        self.assertEqual(kwargs["params"]["destination"], "LAX")

    @patch("app.requests.get")
    def test_fetch_api_data_error(self, mock_get):
        """Test API error handling."""
        # Mock error response
        mock_get.side_effect = Exception("API Error")

        # Call function
        result = fetch_api_data("JFK", "LAX", "2023-07-15", "2023-07-22")

        # Assertions
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()

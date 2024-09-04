import unittest

from src.update_index import (calculate_index, fetch_api_years,
                              impute_missing_values, normalize)

sample_api_data = [
    {"Year": "2020", "Population": 1000, "Household Income": 50000},
    {"Year": "2021", "Population": 1100, "Household Income": 51000},
]

sample_historical_data = [
    {"year": 2019, "Population": 900, "Household Income": 49000}
]

class TestUpdateIndex(unittest.TestCase):

    def test_normalize(self):
        # Basic normalization tests
        self.assertEqual(normalize(50, 0, 100), 0.5)
        self.assertEqual(normalize(50, 50, 50), 0)  # Degenerate case
        self.assertEqual(normalize(100, 0, 100), 1)
        self.assertEqual(normalize(0, 0, 100), 0)

    def test_impute_missing_values(self):
        # Present value should be retained
        item = {"Population": 1000}
        self.assertEqual(impute_missing_values(item, sample_historical_data, "Population"), 1000)

        # Missing value should be imputed from historical data
        item = {}
        self.assertEqual(impute_missing_values(item, sample_historical_data, "Population"), 900)

        # Missing key should default to 0 if not found in historical data
        self.assertEqual(impute_missing_values(item, sample_historical_data, "NonexistentKey"), 0)

    def test_calculate_index(self):
        # Test index calculation for multiple years of data
        index_data = calculate_index(sample_api_data, sample_historical_data)
        self.assertEqual(len(index_data), 2)
        
        # Ensure expected keys are present
        self.assertIn("year", index_data[0])
        self.assertIn("index_value", index_data[0])

        # Check if index values are within expected bounds
        self.assertTrue(0 <= index_data[0]["index_value"] <= 1)
        self.assertTrue(0 <= index_data[1]["index_value"] <= 1)

    def test_fetch_api_years(self):
        # Ensure correct years are fetched from API data
        self.assertEqual(fetch_api_years(sample_api_data), {2020, 2021})

if __name__ == "__main__":
    unittest.main()

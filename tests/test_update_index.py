import unittest
from unittest.mock import patch, MagicMock
from src.update_index import fetch_data_from_api, update_index_in_db, log_error

class TestUpdateIndex(unittest.TestCase):

    @patch('src.update_index.requests.get')
    def test_fetch_data_from_api_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"index_value": 50}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        data = fetch_data_from_api()
        self.assertEqual(data["index_value"], 50)

    @patch('src.update_index.mysql.connector.connect')
    def test_update_index_in_db(self, mock_connect):
        mock_db = mock_connect.return_value
        mock_cursor = mock_db.cursor.return_value

        data = {"index_value": 50}
        update_index_in_db(data)

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO index_table (date, index_value) VALUES (%s, %s)",
            (unittest.mock.ANY, 50)
        )

    @patch('src.update_index.log_error')
    def test_fetch_data_from_api_failure(self, mock_log_error):
        with patch('src.update_index.requests.get', side_effect=Exception("API Error")):
            data = fetch_data_from_api()
            self.assertIsNone(data)
            mock_log_error.assert_called_with("API request failed: API Error")

if __name__ == "__main__":
    unittest.main()

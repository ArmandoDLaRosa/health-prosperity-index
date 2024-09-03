import pytest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime
from src.update_index import update_index_in_db, calculate_prosperity_index, fetch_data_from_api, log_error

# Mocking the API call for fetch_data_from_api
@patch('your_script_name.requests.get')
def test_fetch_data_from_api(mock_get):
    # Mock the API response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "data": [{"Year": 2022, "Population": 2500000000, "Household Income": 800000000, "Average Wage": 25000}]
    }

    # Call the function (URL doesn't matter because requests.get is mocked)
    data = fetch_data_from_api("https://datausa.io/api/data?measures=Population,Household%20Income,Average%20Wage")
    
    # Validate that the data fetched is as expected
    assert len(data) == 1
    assert data[0]["Year"] == 2022
    assert data[0]["Population"] == 2500000000
    assert data[0]["Household Income"] == 800000000
    assert data[0]["Average Wage"] == 25000

    # Ensure the mock was called as expected
    mock_get.assert_called_once_with("https://datausa.io/api/data?measures=Population,Household%20Income,Average%20Wage")

# Test for calculate_prosperity_index function
def test_calculate_prosperity_index():
    record = {
        "Population": 2500000000,
        "Household Income": 800000000,
        "Average Wage": 25000
    }
    min_values = {
        "Population": 2400000000,
        "Household Income": 780000000,
        "Average Wage": 20000
    }
    max_values = {
        "Population": 2600000000,
        "Household Income": 850000000,
        "Average Wage": 30000
    }

    # Manually calculated expected index value
    expected_index = (0.5 + 0.3077 + 0.5) / 3

    result = calculate_prosperity_index(record, min_values, max_values)
    
    # Allow a small margin of error for floating-point calculations
    assert pytest.approx(result, 0.001) == expected_index

# Mocking the database connection and cursor for update_index_in_db
@patch('your_script_name.mysql.connector.connect')
def test_update_index_in_db(mock_connect):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_connect.return_value = mock_conn

    record = {"Year": 2022}
    index_value = 0.75

    # Execute the function to update the index in the database
    update_index_in_db(record, index_value)

    # Verify the SQL execution with correct parameters
    mock_cursor.execute.assert_called_once_with(
        """
        INSERT INTO index_table (year, index_value, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            index_value = VALUES(index_value),
            updated_at = VALUES(updated_at)
        """,
        (2022, index_value, ANY, ANY)
    )

    # Ensure the commit was made to the database
    mock_conn.commit.assert_called_once()

    # Ensure that the cursor and connection are closed after execution
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

# Testing logging functionality
@patch('your_script_name.open', new_callable=MagicMock)
def test_log_error(mock_open):
    log_error("Test error message")

    # Verify that the log file is opened correctly
    mock_open.assert_called_once_with("/var/log/app_errors.log", "a")
    
    # Ensure that the error message is correctly formatted and written to the log
    mock_open.return_value.write.assert_called_once_with(f"{datetime.now()} - ERROR - Test error message\n")

# Running the tests
if __name__ == "__main__":
    pytest.main()

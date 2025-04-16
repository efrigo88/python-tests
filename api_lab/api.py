import requests
import json
import os
from typing import Dict, Any


class JSONPlaceholderClient:
    """Class to handle JSONPlaceholder API interactions."""

    def __init__(self):
        """Initialize the JSONPlaceholder client."""
        self.base_url = "https://jsonplaceholder.typicode.com"

    def get_albums(self) -> Dict[str, Any]:
        """Fetch albums data from JSONPlaceholder API.

        Returns:
            Dict[str, Any]: Raw JSON response from the API
        """
        url = f"{self.base_url}/albums"
        response = requests.get(url)

        if response.status_code != 200:
            raise requests.exceptions.RequestException(
                f"API request failed with status code {response.status_code}: "
                f"{response.text}"
            )

        return response.json()

    def save_albums(self, albums_data: Dict[str, Any], filepath: str) -> None:
        """Save albums data to a JSON file.

        Args:
            albums_data (Dict[str, Any]): Albums data to save
            filepath (str): Path where to save the JSON file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(albums_data, f, indent=2)
        print(f"Albums data saved successfully to {filepath}")


def main():
    """Main function to run the data processing pipeline."""
    try:
        # Get data from JSONPlaceholder API
        api_client = JSONPlaceholderClient()
        albums_data = api_client.get_albums()
        print(f"Successfully fetched {len(albums_data)} albums")

        # Save the data
        api_client.save_albums(albums_data, "data/albums.json")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
    except (IOError, OSError) as e:
        print(f"File operation failed: {str(e)}")


if __name__ == "__main__":
    main()

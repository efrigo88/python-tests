import sys
import json
import requests
from typing import List, Optional


def ask_question(options: List[str]) -> Optional[str]:
    print("For which environment would you like to refresh connections?")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def _get_workspaces(airbyte_base_url: str) -> dict:
    url = f"{airbyte_base_url}/v1/workspaces/list"
    response = requests.post(url)

    if response.status_code == 200:
        return response.json()
    raise ValueError(response.json()["message"])


def _get_workspace_id(airbyte_base_url: str) -> str:
    workspaces = _get_workspaces(airbyte_base_url).get("workspaces", [])
    if len(workspaces) > 0:
        return workspaces[0].get("workspaceId", None)
    return None


def find_all_connections(airbyte_base_url: str) -> list:
    payload = {"workspaceId": _get_workspace_id(airbyte_base_url)}
    url = f"{airbyte_base_url}/v1/connections/list"

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise ValueError(response.json()["message"])

    connections = response.json().get("connections", [])
    return [connection for connection in connections]


# Select the environment to set airbyte_base_url
options_list = ["dev", "prod", "exit"]
env = ask_question(options_list)
print(f"You selected: {env}")

if env == "dev":
    airbyte_base_url = "http://ec2-79-125-101-195.eu-west-1.compute.amazonaws.com/api"
elif env == "prod":
    airbyte_base_url = "http://ec2-52-16-71-181.eu-west-1.compute.amazonaws.com/api"
else:
    print("No environment has been selected, exiting...")
    sys.exit()

# Get all airbyte connections and filter the relevant ones
data = []
all_connections = find_all_connections(airbyte_base_url)
print(f"Total number of Airbyte connections: {len(all_connections)}")

# Iterate through each element in the list
for element in all_connections:
    if "ListFinancialEvents" in element["name"]:
        data.append(
            {
                "name": element["name"],
                "sourceId": element["sourceId"],
                "connectionId": element["connectionId"],
            }
        )
print(f"Number of financial event connections: {len(data)} detected")

# Convert the list of dictionaries to JSON format
data_json = json.dumps(data, indent=2)

# Write the JSON data to a file
path = f"dags/amazon_pipelines_config/financial_events_airbyte_connections/connections_{env}.json"
with open(path, "w") as json_file:
    json_file.write(data_json)

print(f"JSON data has been written in path: {path}")
print("Process finished successfully!")

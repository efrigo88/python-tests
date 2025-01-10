import json
from flask import Flask, jsonify

app = Flask(__name__)

# Load sample data from file
with open("bamboohr_fake_sample_data/mock_bamboohr_data.json", "r") as f:
    mock_data = json.load(f)


@app.route("/api/payclip/v1/employees/directory", methods=["GET"])
def get_employees_directory():
    return jsonify(mock_data)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

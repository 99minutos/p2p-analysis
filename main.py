from flask import Flask, request, jsonify

from p99 import belongs_to_p99
from process import process_and_update, process_entries
import os

app = Flask(__name__)


@app.route('/process', methods=['POST'])
def process_json():
    try:
        data = request.get_json()  # Get the JSON data from the request
        process_and_update(data)  # Process the data
        return {}, 200
    except Exception as e:
        print(e)
        # Handle any exceptions that occurred during processing
        result = {'status': 'error', 'message': str(e)}
        return jsonify(result), 204


@app.route('/belongs_to_p99', methods=['POST'])
def belongs_to_p99_controller():
    try:
        data = request.get_json()  # Get the JSON data from the request
        has_p99 = belongs_to_p99(data)  # Process the data
        return {}, 200
    except Exception as e:
        print(e)
        # Handle any exceptions that occurred during processing
        result = {'status': 'error', 'message': str(e)}
        return jsonify(result), 204


@app.route('/queue', methods=['GET'])
async def enqueue():
    await process_entries()
    return {}, 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

from flask import Flask, request, jsonify
from process import process_and_update
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


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

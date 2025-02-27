from flask import Flask, request
from flask_cors import CORS
import os
from generate_report import generate_pdf  # Import the fixed function

app = Flask(__name__)
CORS(app)

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf_route():
    ticker = request.args.get('ticker')
    if not ticker:
        return "Ticker is required", 400
    return generate_pdf(ticker)  # Call the fixed function


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)


if __name__ == '__main__':
    app.run(debug=True)
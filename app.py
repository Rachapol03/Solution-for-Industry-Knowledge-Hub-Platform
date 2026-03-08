import os

# Render runs the service with `python app.py`. This file is the entrypoint.
# The Flask app is defined in main.py.
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Index static file
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')
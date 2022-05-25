import datetime
import hashlib
import json
from flask import Flask, jsonify


class Blockchain:
    def __init__(self):
        self.chain = []

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

from flask import Flask
from flask_cors import CORS

from ..reader.base import TraceReader


def create_app(reader: TraceReader):
    app = Flask(__name__)
    CORS(app)

    @app.route("/list")
    def list():
        return reader.list_summaries()

    @app.route("/traces/<trace_id>")
    def get_trace(trace_id: str):
        return reader.read_trace(trace_id)

    return app

from flask import Flask
from flask_cors import CORS

from ..reader.base import TraceReader
from ..html.staticfiles import read_index, STATIC_FILE_DIR


def create_app(reader: TraceReader, port):
    app = Flask(__name__, static_url_path="/assets", static_folder=STATIC_FILE_DIR)
    CORS(app)

    @app.route("/api/list")
    def list():
        return reader.list_summaries()

    @app.route("/api/traces/<trace_id>")
    def get_trace(trace_id: str):
        return reader.read_trace(trace_id)

    @app.route("/traces/<trace_id>")
    @app.route("/")
    def get_index(trace_id: str | None = None):
        content = read_index()
        content = content.replace("%%%URL%%%", f"http://localhost:{port}/")
        return content

    return app


def start_server(reader: TraceReader, host: str = "localhost", port: int = 4090, debug: bool = False):
    application = create_app(reader, port)
    if debug:
        application.run(host=host, port=port, debug=True)
    else:
        from waitress import serve
        print(f"Running at http://localhost:{port}")
        serve(application, host=host, port=port)


def start_server_in_jupyter(reader: TraceReader, port: int = 4090, debug: bool = False):
    from IPython.lib import backgroundjobs as bg
    jobs = bg.BackgroundJobManager()
    jobs.new(lambda: start_server(reader, port=port, debug=debug))

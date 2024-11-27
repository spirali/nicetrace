from flask import Flask
from flask_cors import CORS

from ..reader.base import TraceReader
from ..html.staticfiles import read_index, STATIC_FILE_DIR


def create_app(reader: TraceReader, server_name):
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
        content = content.replace("%%%URL%%%", server_name)
        return content

    return app


def start_server(
    reader: TraceReader,
    host: str = "localhost",
    server_name: str | None = None,
    port: int = 4090,
    debug: bool = False,
    verbose: bool = True,
):
    """
    This needs feature "server".
    Starts a HTTP server over a given trace reader. It blocks the process.
    """
    if server_name is None:
        server_name = f"http://localhost:{port}/"
    elif not server_name.endswith("/"):
        server_name += "/"
    application = create_app(reader, server_name)
    if debug:
        application.run(host=host, port=port, debug=True)
    else:
        from waitress import serve

        if verbose:
            print(f"Running at {server_name}")
        serve(application, host=host, port=port)


def start_server_in_jupyter(reader: TraceReader, port: int = 4090, debug: bool = False):
    """
    This needs feature "server".
    Starts a HTTP server over a given trace reader. Stars a server as jupyter background process.
    """

    from IPython.lib import backgroundjobs as bg

    try:
        # Running in Google Colab
        from google.colab.output import eval_js

        server_name = str(eval_js(f"google.colab.kernel.proxyPort({port})"))
        print(f"Running at {server_name}")
        host = "0.0.0.0"
        verbose = False
    except ImportError:
        # Running in normal jupyter notebook
        server_name = None
        host = "localhost"
        verbose = True
    jobs = bg.BackgroundJobManager()
    jobs.new(
        lambda: start_server(
            reader,
            port=port,
            debug=debug,
            server_name=server_name,
            host=host,
            verbose=verbose,
        )
    )

    # if inline_colab:
    #     import IPython.display
    #
    #     return IPython.display.Javascript(
    #         """
    #         (async ()=>{{
    #             fm = document.createElement('iframe')
    #             fm.src = await google.colab.kernel.proxyPort({port})
    #             fm.width = '90%'
    #             fm.height = '1024'
    #             fm.frameBorder = 0
    #             fm.style = 'background: white;'
    #             document.body.append(fm)
    #         }})();
    #     """.format(port=port)
    #     )

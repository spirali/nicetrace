from http.server import ThreadingHTTPServer
import argparse

from .app import create_app
from ..reader.filereader import FileReader
from waitress import serve


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=6040)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    reader = FileReader(args.path)
    application = create_app(reader)
    if args.debug:
        application.run(host=args.host, port=args.port, debug=True)
    else:
        print(f"Running at http://localhost:{args.port}")
        serve(application, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

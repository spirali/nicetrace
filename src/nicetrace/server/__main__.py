import argparse

from ..reader.filereader import DirReader
from .app import start_server


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=6040)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    reader = DirReader(args.path)
    start_server(reader, host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()

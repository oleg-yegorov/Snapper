import argparse
import logging
from pathlib import Path

import urllib3
import yaml
from aiohttp.web import run_app
from urllib3.exceptions import InsecureRequestWarning

from snapper.app import create_app

# disable warnings
urllib3.disable_warnings(InsecureRequestWarning)


# --------------------------MAIN------------------------- #
def build_parser() -> argparse.ArgumentParser:
    conf_parser = argparse.ArgumentParser(
        # Turn off help, so we print all options in response to -h
        add_help=False
    )
    conf_parser.add_argument("-c", "--config", dest="config", action="store",
                             help="Specify config file", metavar="FILE",
                             default=Path(__file__).parent / "config.yaml")
    args, remaining_argv = conf_parser.parse_known_args()
    defaults = {}
    if not args.config:
        raise Exception("Config file not specified (use -c/--config)")

    with open(args.config, "r") as file:
        defaults.update(yaml.safe_load(file))

    parser = argparse.ArgumentParser(parents=[conf_parser])
    parser.set_defaults(**defaults)
    parser.add_argument("-u", '--user-agent', action='store',
                        dest="user_agent", type=str,
                        help='The user agent used for requests')
    parser.add_argument("-f", "--output_paths_format", action="store",
                        dest="output_paths_format", type=str,
                        help="Format applied to output paths")
    parser.add_argument("-tt", "--task_timeout_sec", action="store",
                        dest="task_timeout_sec", type=int,
                        help="Format applied to output paths")
    parser.add_argument("-o", '--output', action='store',
                        dest="output_dir", type=str,
                        help='Directory for output')
    parser.add_argument("-l", '--log_level', action='store',
                        dest="log_level", type=str,
                        help='Logging facility level')
    parser.add_argument("-w", '--workers', action='store', 
                        dest="workers", type=int, 
                        help='Number of cuncurrent processes')
    parser.add_argument("-t", '--timeout', action='store',
                        dest="timeout", type=int,
                        help='Number of seconds to try to resolve')
    parser.add_argument("-p", '--port', action='store',
                        dest="port", type=str, default=defaults["app"]["port"],
                        help='Port to run server on')
    parser.add_argument("-H", '--host', action='store',
                        dest="host", type=str, default=defaults["app"]["host"],
                        help='Host to run server on')
    parser.add_argument("-v", action='store_true', dest="verbose",
                        help='Display console output for fetching each host')
    parser.add_argument("--aws_bucket_name", action='store',
                        dest='aws_bucket_name', help='AWS bucket name')
    return parser


def setup_logger(log_level):
    try:
        logging.basicConfig(level=log_level)
    except ValueError:
        raise argparse.ArgumentTypeError('Unknown log level'.format(key=log_level)) from None


def main():
    args, remaining_argv = build_parser().parse_known_args()
    setup_logger(args.log_level)

    app = create_app(args)
    run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

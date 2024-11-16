from dotenv import load_dotenv
from postgres import PostgresDB
import os
import random
import argparse
import json
from server import create_app

load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description='Poll data exporter')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Server command
    server_parser = subparsers.add_parser('server', help='Run in server mode')
    server_parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    server_parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')

    # CLI command
    cli_parser = subparsers.add_parser('cli', help='Run in CLI mode')
    cli_parser.add_argument('--chain', type=str, required=True, help='Chain name (sepolia/mainnet/base/etc.)')
    cli_parser.add_argument('--address', type=str, required=True, help='Chain address of the target poll')
    cli_parser.add_argument('--output', type=str, required=True, help='Output JSON file name')

    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.command == 'server':
        app = create_app()
        app.run(host=args.host, port=args.port)
    else:
        pass

if __name__ == '__main__':
    main()
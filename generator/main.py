from dotenv import load_dotenv
from postgres import PostgresDB
import os
import random
import argparse
import json
import logging
from server import create_app
from math_calculator import calculate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    cli_parser.add_argument('--address', type=str, required=True, help='Chain address of the target conversation')
    cli_parser.add_argument('--output', type=str, required=True, help='Output JSON file name')

    return parser.parse_args()

def main():
    args = parse_args()
    #db_host = os.getenv('POSTGRES_HOST')
    db_host = 'localhost'
    db_port = int(os.getenv('POSTGRES_PORT') or 5432)
    database = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    database_url = f'postgres://{user}:{password}@{db_host}:{db_port}/{database}'
    
    if args.command == 'server':
        app = create_app()
        app.run(host=args.host, port=args.port)
    else:
        zid = 1
        calculate(database_url, zid, working_dir='../math')

if __name__ == '__main__':
    main()
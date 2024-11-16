from dotenv import load_dotenv
from postgres import PostgresDB
import os
import random
import argparse
import json
import logging
from server import create_app
from math_calculator import calculate
from conv_fetcher import ConvFetcher

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
    math_dir = '../math'
    #db_host = os.getenv('POSTGRES_HOST')
    db_host = 'localhost'
    db_port = os.getenv('POSTGRES_PORT', 5432)
    database = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    database_url = f'postgres://{user}:{password}@{db_host}:{db_port}/{database}'
    
    if args.command == 'server':
        app = create_app(db_host, database, user, password, db_port=db_port, math_dir=math_dir)
        app.run(host=args.host, port=args.port)
    else:
        db = PostgresDB(host=db_host, database=database, user=user, password=password, port=db_port)
        fetcher = ConvFetcher(args.chain)
        data = fetcher.fetch(args.address)
        zid = db.add_conversation_data_from_dict(data)

        # 2 times
        calculate(database_url, zid, working_dir=math_dir)
        calculate(database_url, zid, working_dir=math_dir)
        #zid = 1
        math_data = db.get_math_data(zid)
        logger.debug(math_data)
        with open(args.output, 'w') as f:
            json.dump(math_data, f)
        logger.info(f"Math data saved to {args.output}")

if __name__ == '__main__':
    main()
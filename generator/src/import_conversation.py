import sys
import os
import json

from dotenv import load_dotenv
from postgres import PostgresDB
from math_calculator import calculate

load_dotenv()

db_host = os.getenv('POSTGRES_HOST', 'localhost')
db_port = os.getenv('POSTGRES_PORT', 5432)
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
database_url = f'postgres://{user}:{password}@{db_host}:{db_port}/{database}'
print("database_url", database_url)

if len(sys.argv) < 2:
    print("Usage: python populate_data.py <data json file>")
    sys.exit(1)

db = PostgresDB(
    host='localhost',
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

topic = data['title']
description = data['description']
statements = data['statements']
votes = data['votes']

users = {}
for vote in votes:
    users[vote['voter']] = db.ensure_user(vote['voter'])

zid = db.create_conversation(
    topic=topic,
    description=description,
    owner=users[votes[0]['voter']],
    address="0x0000000000000000000000000000000000000000",
    chain="ethereum"
)

for statement in statements:
    tid = db.create_comment(
        zid=zid,
        uid=users[votes[0]['voter']],
        txt=statement['text']
    )

for vote in votes:
    db.create_vote(
        zid=zid,
        uid=users[vote['voter']],
        tid=vote['statement_id'],
        vote=vote['value']
    )

conversation = db.get_conversation(zid)
print("conversation", conversation)
comments = db.get_comments(zid)
print("comments", comments)
votes = db.get_all_votes(zid)
print("votes", votes)
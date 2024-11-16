import sys
import os
import json

from dotenv import load_dotenv
from postgres import PostgresDB

load_dotenv()

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

topic = data['topic']
description = data['description']
statements = data['statements']
participants = data['participants']


pids = {}
for pid, participant in participants.items():
    pids[int(pid)] = db.ensure_user(participant['address'])

zid = db.create_conversation(
    topic="Discussion Topic",
    description="Discussion Description",
    owner=pids[0]
)

for statement in statements:
    tid = db.create_comment(
        zid=zid,
        uid=pids[int(statement['pid'])],
        txt=statement['txt']
    )

for pid, participant in participants.items():
    for i in range(len(participant['votes'])):
        db.create_vote(
            zid=zid,
            uid=pids[int(pid)],
            tid=i,
            vote=participant['votes'][i]
        )

conversation = db.get_conversation(zid)
print("conversation", conversation)
comments = db.get_comments(zid)
print("comments", comments)
votes = db.get_all_votes(zid)
print("votes", votes)

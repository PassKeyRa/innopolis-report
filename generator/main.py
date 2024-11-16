from dotenv import load_dotenv
from postgres import PostgresDB
import os
import random

load_dotenv()

db = PostgresDB(
    host='localhost',
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

random_mail = lambda: f"user{random.randint(1000, 9999)}@example.com"

# First create a user
uid = db.create_user(
    address=random_mail(),
    hname=f"Example User {random.randint(1000, 9999)}",
    is_owner=True  # Give them conversation creation privileges
)

# Then create a conversation owned by that user
zid = db.create_conversation(
    topic="Discussion Topic",
    description="Discussion Description",
    owner=uid
)

# Create a comment
tid = db.create_comment(
    zid=zid,
    uid=uid,
    txt="This is a comment"
)

# Create a vote
db.create_vote(
    zid=zid,
    uid=uid,
    tid=tid,
    vote=1
)

# Create a second user
uid2 = db.create_user(
    address=random_mail(),
    hname=f"Example User {random.randint(1000, 9999)}",
    is_owner=False  # Give them conversation creation privileges
)

# Create a vote
db.create_vote(
    zid=zid,
    uid=uid2,
    tid=tid,
    vote=-1
)

# Create a second user
uid3 = db.create_user(
    address=random_mail(),
    hname=f"Example User {random.randint(1000, 9999)}",
    is_owner=False  # Give them conversation creation privileges
)

# Create a vote
db.create_vote(
    zid=zid,
    uid=uid3,
    tid=tid,
    vote=-1
)

# Get conversation details
conversation = db.get_conversation(zid)
print(conversation)
comments = db.get_comments(zid)
print(comments)
votes = db.get_votes(zid, tid)
print(votes)

# Close connection when done
db.close()
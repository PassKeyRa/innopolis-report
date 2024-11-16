import psycopg2
from typing import Dict, List, Optional, Union
from datetime import datetime

class PostgresDB:
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        """Initialize PostgreSQL database connection"""
        self.conn_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.conn = None
        self.connect()

    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            raise Exception(f"Failed to connect to database: {e}")

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()

    # Conversation Methods
    def create_conversation(self, topic: str, description: str, owner: int) -> int:
        """Create a new conversation and return its zid"""
        try:
            # First check if owner exists
            user = self.get_user(owner)
            if not user:
                raise Exception(f"User with uid {owner} does not exist")
            if not user['is_owner']:
                raise Exception(f"User with uid {owner} does not have conversation creation privileges")

            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO conversations 
                    (topic, description, owner) 
                    VALUES (%s, %s, %s) 
                    RETURNING zid
                """, (topic, description, owner))
                zid = cur.fetchone()[0]
                self.conn.commit()
                return zid
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create conversation: {e}")

    def get_conversation(self, zid: int) -> Optional[Dict]:
        """Get conversation details by zid"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT zid, topic, description, owner, created, participant_count 
                    FROM conversations 
                    WHERE zid = %s
                """, (zid,))
                result = cur.fetchone()
                if result:
                    return {
                        'zid': result[0],
                        'topic': result[1],
                        'description': result[2],
                        'owner': result[3],
                        'created': result[4],
                        'participant_count': result[5]
                    }
                return None
        except psycopg2.Error as e:
            raise Exception(f"Failed to get conversation: {e}")

    # Comment Methods
    def _ensure_participant(self, zid: int, uid: int) -> int:
        """Get participant ID or create if doesn't exist"""
        pid = self.get_participant_id(zid, uid)
        if pid is None:
            pid = self.create_participant(zid, uid)
        return pid

    def create_comment(self, zid: int, uid: int, txt: str) -> int:
        """Create a new comment and return its tid"""
        try:
            pid = self._ensure_participant(zid, uid)
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO comments 
                    (zid, pid, uid, txt) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING tid
                """, (zid, pid, uid, txt))
                tid = cur.fetchone()[0]
                self.conn.commit()
                return tid
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create comment: {e}")

    def get_comments(self, zid: int) -> List[Dict]:
        """Get all comments for a conversation"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT tid, pid, uid, txt, created, mod 
                    FROM comments 
                    WHERE zid = %s 
                    ORDER BY tid
                """, (zid,))
                return [{
                    'tid': row[0],
                    'pid': row[1],
                    'uid': row[2],
                    'txt': row[3],
                    'created': row[4],
                    'mod': row[5]
                } for row in cur.fetchall()]
        except psycopg2.Error as e:
            raise Exception(f"Failed to get comments: {e}")

    # Vote Methods
    def _ensure_participant(self, zid: int, uid: int) -> int:
        """Get participant ID or create if doesn't exist"""
        pid = self.get_participant_id(zid, uid)
        if pid is None:
            pid = self.create_participant(zid, uid)
        return pid

    def create_vote(self, zid: int, uid: int, tid: int, vote: int) -> None:
        """Create a new vote"""
        try:
            pid = self._ensure_participant(zid, uid)
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO votes 
                    (zid, pid, tid, vote) 
                    VALUES (%s, %s, %s, %s)
                """, (zid, pid, tid, vote))
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create vote: {e}")

    def get_votes(self, zid: int, tid: int) -> List[Dict]:
        """Get all votes for a specific comment"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT pid, vote, modified 
                    FROM votes_latest_unique 
                    WHERE zid = %s AND tid = %s
                """, (zid, tid))
                return [{
                    'pid': row[0],
                    'vote': row[1],
                    'modified': row[2]
                } for row in cur.fetchall()]
        except psycopg2.Error as e:
            raise Exception(f"Failed to get votes: {e}")
    
    def get_all_votes(self, zid: int) -> List[Dict]:
        """Get all votes for a conversation"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT zid, pid, tid, vote, modified 
                    FROM votes_latest_unique 
                    WHERE zid = %s
                """, (zid,))
                return [{
                    'zid': row[0],
                    'pid': row[1],
                    'tid': row[2],
                    'vote': row[3],
                    'modified': row[4]
                } for row in cur.fetchall()]
        except psycopg2.Error as e:
            raise Exception(f"Failed to get all votes: {e}")

    # Participant Methods
    def get_participant_id(self, zid: int, uid: int) -> Optional[int]:
        """Get participant ID for a user in a conversation"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT pid 
                    FROM participants 
                    WHERE zid = %s AND uid = %s
                """, (zid, uid))
                result = cur.fetchone()
                return result[0] if result else None
        except psycopg2.Error as e:
            raise Exception(f"Failed to get participant ID: {e}")

    def create_participant(self, zid: int, uid: int) -> int:
        """Create a new participant and return their pid"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO participants 
                    (zid, uid) 
                    VALUES (%s, %s) 
                    RETURNING pid
                """, (zid, uid))
                pid = cur.fetchone()[0]
                self.conn.commit()
                return pid
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create participant: {e}")

    def create_user(self, address: str, is_owner: bool = True) -> int:
        """Create a new user and return their uid"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users 
                    (address, is_owner) 
                    VALUES (%s, %s) 
                    RETURNING uid
                """, (address, is_owner))
                uid = cur.fetchone()[0]
                self.conn.commit()
                return uid
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create user: {e}")
    
    def get_user_id(self, address: str) -> Optional[int]:
        """Get user ID by address"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT uid 
                    FROM users 
                    WHERE address = %s
                """, (address,))
                result = cur.fetchone()
                return result[0] if result else None
        except psycopg2.Error as e:
            raise Exception(f"Failed to get user ID: {e}")
    
    def ensure_user(self, address: str) -> int:
        """Ensure a user exists and return their uid"""
        uid = self.get_user_id(address)
        if uid is None:
            uid = self.create_user(address)
        return uid

    def get_user(self, uid: int) -> Optional[Dict]:
        """Get user details by uid"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT uid, address, is_owner, created 
                    FROM users 
                    WHERE uid = %s
                """, (uid,))
                result = cur.fetchone()
                if result:
                    return {
                        'uid': result[0],
                        'address': result[1],
                        'is_owner': result[2],
                        'created': result[3]
                    }
                return None
        except psycopg2.Error as e:
            raise Exception(f"Failed to get user: {e}")

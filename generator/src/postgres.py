import psycopg2
from typing import Dict, List, Optional, Union, Any
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
    
    def add_conversation_data_from_dict(self, data: Dict) -> int:
        """Add conversation data from dictionary to database"""
        try:
            # First ensure all users exist
            users = {data['creator']}  # Start with creator
            for statement in data['statements']:
                users.add(statement['author'])
            for vote in data.get('votes', []):  # Safely handle if votes don't exist
                users.add(vote['voter'])
            
            # Create all users that don't exist yet
            for address in users:
                self.ensure_user(address)
            
            # Create conversation
            creator_uid = self.get_user_id(data['creator'])
            zid = self.create_conversation(
                topic=data['title'],
                description=data['description'],
                owner=creator_uid,
                address=data['address'],
                chain=data['chain']
            )
            
            # Add statements as comments
            for statement in data['statements']:
                author_uid = self.get_user_id(statement['author'])
                tid = self.create_comment(
                    zid=zid,
                    uid=author_uid,
                    txt=statement['content']
                )
            
            # Add votes
            for vote in data.get('votes', []):
                voter_uid = self.get_user_id(vote['voter'])
                # Convert vote type: 1 = Agree, 2 = Disagree
                vote_type = 1 if vote['vote'] == 1 else -1 if vote['vote'] == 2 else 0
                self.create_vote(
                    zid=zid,
                    uid=voter_uid,
                    tid=vote['statementId'],
                    vote=vote_type
                )
            
            self.conn.commit()
            return zid
            
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Failed to add conversation data: {e}")
    
    def get_math_data(self, zid: int) -> Dict[str, Any]:
        """Get math data for a conversation from math_main table"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT data 
                    FROM math_main 
                    WHERE zid = %s 
                    ORDER BY math_tick DESC 
                    LIMIT 1
                """, (zid,))
                
                result = cur.fetchone()
                if result:
                    return result[0]  # Return the JSON data directly
                return {}
                
        except psycopg2.Error as e:
            raise Exception(f"Failed to get math data: {e}")

    # Conversation Methods
    def create_conversation(self, topic: str, description: str, owner: int, address: Optional[str] = None, chain: Optional[str] = None) -> int:
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
                    (topic, description, owner, address, chain) 
                    VALUES (%s, %s, %s, %s, %s) 
                    RETURNING zid
                """, (topic, description, owner, address, chain))
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
                    SELECT zid, topic, description, owner, created, participant_count, address, chain 
                    FROM conversations 
                    WHERE zid = %s
                """, (zid,))
                result = cur.fetchone()
                if result:
                    return {
                        'conversation_id': result[0],
                        'topic': result[1],
                        'description': result[2],
                        'owner': result[3],
                        'created': result[4],
                        'participant_count': result[5],
                        'address': result[6],
                        'chain': result[7]
                    }
                return None
        except psycopg2.Error as e:
            raise Exception(f"Failed to get conversation: {e}")

    def get_conversation_by_address_and_chain(self, address: str, chain: str) -> Optional[Dict]:
        """Get conversation details by blockchain address and chain, returns the most recent one if multiple exist"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT zid, topic, description, owner, created, participant_count, address, chain 
                    FROM conversations 
                    WHERE address = %s AND chain = %s
                    ORDER BY zid DESC
                    LIMIT 1
                """, (address, chain))
                result = cur.fetchone()
                if result:
                    return {
                        'conversation_id': result[0],
                        'topic': result[1],
                        'description': result[2],
                        'owner': result[3],
                        'created': result[4],
                        'participant_count': result[5],
                        'address': result[6],
                        'chain': result[7]
                    }
                return None
        except psycopg2.Error as e:
            raise Exception(f"Failed to get conversation by address: {e}")

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
        """Get all comments for a conversation with vote counts"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.tid, 
                        c.pid, 
                        c.uid, 
                        c.txt, 
                        c.created, 
                        c.modified, 
                        c.mod, 
                        c.is_seed,
                        COALESCE(SUM(CASE WHEN v.vote = 1 THEN 1 ELSE 0 END), 0) as agree_count,
                        COALESCE(SUM(CASE WHEN v.vote = -1 THEN 1 ELSE 0 END), 0) as disagree_count,
                        COALESCE(SUM(CASE WHEN v.vote = 0 THEN 1 ELSE 0 END), 0) as pass_count,
                        COUNT(v.vote) as total_votes
                    FROM comments c
                    LEFT JOIN votes_latest_unique v ON c.zid = v.zid AND c.tid = v.tid
                    WHERE c.zid = %s 
                    GROUP BY c.tid, c.pid, c.uid, c.txt, c.created, c.modified, c.mod, c.is_seed
                    ORDER BY c.tid
                """, (zid,))
                
                comments = []
                for row in cur.fetchall():
                    comments.append({
                        'active': True,
                        'conversation_id': zid,
                        'tid': row[0],
                        'pid': row[1],
                        'uid': row[2],
                        'txt': row[3],
                        'created': row[4],
                        'modified': row[5],
                        'mod': row[6],
                        'is_seed': row[7],
                        'agree_count': row[8],
                        'disagree_count': row[9],
                        'pass_count': row[10],
                        'count': row[11]
                    })
                return comments
                
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


from web3 import Web3
from web3.contract import Contract
from eth_abi import decode
from pathlib import Path
from typing import Dict, Any
from config import CHAINS
import json

class ConvFetcher:
    def __init__(self, chain: str):
        if chain not in CHAINS:
            raise ValueError(f"Unsupported chain: {chain}")
        
        self.w3 = Web3(Web3.HTTPProvider(CHAINS[chain]['rpcTarget']))
        self.chain = chain

        # Load ABI
        abi_path = Path(__file__).parent / "abi" / "IConversation.sol"
        with open(abi_path) as f:
            self.abi = json.load(f)

    def fetch(self, contract_address: str) -> Dict[str, Any]:
        if not self.w3.is_address(contract_address):
            raise ValueError(f"Invalid contract address: {contract_address}")
            
        contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(contract_address),
            abi=self.abi
        )
        
        # Prepare multicall data
        calls = [
            contract.encode_abi('title', []),
            contract.encode_abi('description', []),
            contract.encode_abi('creator', []),
            contract.encode_abi('deadline', []),
            contract.encode_abi('statementCount', []),
            contract.encode_abi('voteCount', [])
        ]
        
        # Execute multicall
        results = contract.functions.multicall(calls).call()
        
        # Decode basic conversation data
        title = decode(('string',), results[0])[0]
        description = decode(('string',), results[1])[0]
        creator = decode(('address',), results[2])[0]
        deadline = decode(('uint256',), results[3])[0]
        statement_count = decode(('uint256',), results[4])[0]
        votes_count = decode(('uint256',), results[5])[0]
        
        # Prepare calls for statements
        statement_calls = []
        for i in range(statement_count):
            statement_calls.append(contract.encode_abi('statements', [i]))
        
        # Get all statements in one call
        statement_results = contract.functions.multicall(statement_calls).call()
        
        # Decode statements
        statements = []
        for i, result in enumerate(statement_results):
            statement = decode(('address', 'string', 'uint256', 'uint256', 'uint256'), result)
            
            statements_data = {
                'id': i,
                'author': statement[0],
                'content': statement[1],
                'agreeCount': statement[2],
                'disagreeCount': statement[3],
                'timestamp': statement[4]
            }
            statements.append(statements_data)
        
        votes_calls = []
        for i in range(1, votes_count + 1):
            votes_calls.append(contract.encode_abi('votesData', [i]))
        
        votes_results = contract.functions.multicall(votes_calls).call()
        votes = []
        for i, result in enumerate(votes_results):
            vote = decode(('address', 'uint256', 'uint256'), result)
            vote_data = {
                'voter': vote[0],
                'vote': vote[1],
                'statementId': vote[2]
            }
            votes.append(vote_data)

        return {
            'address': contract_address,
            'chain': self.chain,
            'title': title,
            'description': description,
            'creator': creator,
            'deadline': deadline,
            'statements': statements,
            'votes': votes
        }

from ast import Str
import datetime
import hashlib
import http
import json
from typing import Dict
from flask import Flask, jsonify


class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof: str, previous_hash: str):
        block = {
            'block_number': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.chain.append(block)
        return block

    def get_last_block(self) -> str:
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        is_proof_valid = False
        while not is_proof_valid:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()
            ).hexdigest()
            if hash_operation[:4] == '0000':
                is_proof_valid = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block: dict) -> str:
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain) -> bool:
        # We must check 2 things
        # 1. previous_hash of each block is equal to hash of prev block
        # 2. proof of each block is valid according to proof of work function
        previous_block = chain[0]
        block_number = 1
        chain_len = len(chain)
        while block_number < chain_len:
            block = chain[block_number]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            prev_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            block_number += 1
            previous_block = block
        return True


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_last_block()
    proof = blockchain.proof_of_work(prev_block['proof'])
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof, prev_hash)
    message = f'Congratulations, you just mined block {block["block_number"]}'
    return jsonify({**block, 'message': message}), http.HTTPStatus.OK


@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }), http.HTTPStatus.OK

@app.route('/is_valid', methods=['GET'])
def is_valid():
    message = 'Blockchain is valid.' if blockchain.is_chain_valid(
        blockchain.chain) else 'ERROR: Blockchain is invalid!'
    return jsonify({'message': message}), http.HTTPStatus.OK


# Run Flask
app.run(host='0.0.0.0', port=5432)

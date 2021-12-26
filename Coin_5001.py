# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from uuid import uuid4 
import requests
import urllib.parse

class Blockchain:
    
    def __init__(self):
        self.mempool = []
        self.chain = []
        self.nodes = set()
        self.creat_block(proof = 1,previous_hash = '0' )
         
    def creat_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                  'timestamp': str(datetime.datetime.now()),
                  'proof': proof,
                  'previous_hash':previous_hash,
                  'ledger': self.mempool}
        self.chain.append(block)
        self.mempool = []
        return block
    
    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,previous_proof):
        curr_proof = 1
        check_proof = False
        while check_proof is False :
            hash = hashlib.sha256(str(curr_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash[:4] == '0000':
                check_proof = True
            else: 
                curr_proof += 1
        return curr_proof
    
    def hash(self,block):
        # joining various parts of bock to form string
        encode = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encode).hexdigest()
    
    def check_validity(self, chain):
        index = 1
        while index<len(chain):
            previous_block = chain[index - 1]
            previous_hash = self.hash(previous_block)
            proof_of_work_hash = hashlib.sha256(str(chain[index]['proof']**2 - previous_block['proof']**2).encode()).hexdigest()
            
            if chain[index]['previous_hash'] != previous_hash :
                return False
            
            if proof_of_work_hash[:4] != '0000':
                return False
            
            index = index + 1
        return True
    
    def mem_transaction(self,sender,receiver,amount):
        self.mempool.append({'sender':sender,
                             'receiver':receiver,
                             'amount':amount})
        # returning index of the block where transaction will get added
        return self.chain[-1]['index']+1 
    
    def add_node(self,address):
        parsed_url = urllib.parse.urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    # Concencus Protocol
    def fetch_longest_chain(self):
        max_length = len(self.chain)
        flag = False
        for node in self.nodes:
            curr_chain = requests.get('http://'+node+'/full_chain')
            if(curr_chain.status_code == 200 and curr_chain.json()['length']>max_length and self.check_validity(curr_chain.json()['chain'])):
                max_length = curr_chain.json()['length']
                self.chain = curr_chain.json()['chain']
                flag = True
        return flag

# Flask web app
app = Flask(__name__)
 
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

# Mining a block
@app.route('/mine_block',methods=['GET'])   
def mine_block():
    proof = blockchain.proof_of_work(blockchain.get_prev_block()['proof'])
    previous_hash = blockchain.hash(blockchain.get_prev_block())
    blockchain.mem_transaction(sender = node_address, receiver = 'http://127.0.0.1:5001', amount = 1)
    block = blockchain.creat_block(proof, previous_hash)
    response = {'message':'Mining Successful!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'ledger': block['ledger'],
                'previous_hash':block['previous_hash']}
    return jsonify(response), 200

# view full blockchain
@app.route('/full_chain',methods=['GET'])
def full_chain():
    response = {'chain' : blockchain.chain,
                'length':len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/check_validity',methods=['GET'])
def check_validity():
    response = {'Validity':blockchain.check_validity(blockchain.chain)}
    return jsonify(response), 200

@app.route('/new_transaction',methods=['POST'])
def new_transaction():
    json = request.get_json()
    transaction_key = ['sender','receiver','amount']
    if not all (key in json for key in transaction_key ):
        return 'Enter the json file with correct field', 400
    index = blockchain.mem_transaction(json['sender'], json['receiver'], json['amount'])
    return jsonify({'message': f'Transaction will be added to {index}'}), 201

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if json['nodes'] is not None:
        for node in json['nodes']:
            blockchain.add_node(node)
        response = {'message': f'Nodes added Successfully:{len(nodes)}',
                    'nodes': list(blockchain.nodes)}
        return jsonify(response),201 
    return 'Json file is empty', 400

@app.route('/get_longest',methods=['GET'])
def get_longest():
    replaced = blockchain.fetch_longest_chain()
    if replaced:
        return jsonify({'message':'New Chain is : ',
                        'Chain':blockchain.chain}), 200  # Might be some error
    else:
        return jsonify({'message':'Current chain is already the longest.'}), 200
    
# App
app.run(host = '0.0.0.0', port = 5001)
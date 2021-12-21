# """
# @author: Adi Pratap Singh
# pip install Flask==0.12.2
# HTTP Client : Postman
# """

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.creat_block(proof = 1,previous_hash = '0' )
         
    def creat_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                  'timestamp': str(datetime.datetime.now()),
                  'proof': proof,
                  'previous_hash':previous_hash}
        self.chain.append(block)
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

# Flask web app
app = Flask(__name__)

blockchain = Blockchain()

# Mining a block
@app.route('/mine_block',methods=['GET'])   
def mine_block():
    proof = blockchain.proof_of_work(blockchain.get_prev_block()['proof'])
    previous_hash = blockchain.hash(blockchain.get_prev_block())
    block = blockchain.creat_block(proof, previous_hash)
    response = {'message':'Mining Successful!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
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

# App
app.run(host = '0.0.0.0', port = 5000)

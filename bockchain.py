"""
Created on Sun Dec 12 15:20:12 2021

@author: Adi Pratap Singh

pip install Flask==0.12.2
HTTP Client : Postman
"""

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
    

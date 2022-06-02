# import datetime
# import hashlib
# import json
# from flask import Flask, jsonify
# class Blockchain:
#     def __init__(self):
#         self.chain = []

# app = Flask(__name__)
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

import datetime
from datetime import strptime
import hashlib
import json
from flask import Flask, jsonify, request
import requests #pip install request, por seguridad usar python<=3.9
from uuid import uuid4
from urllib.parse import urlparse


#Construir Blockchain

##Para crear criptomoneda - transacciones y funcion de consenso
class Blockchain:

    def __init__(self):
        self.chain = []
        ##Agregar registro de transacciones
        self.transactions = []
        self.createBlock(proof = 1, previousHash = '0')

        #???
        self.block['hash_bloque'] = self.blockHash(self.block)


        ##Agregar nodos para el consenso
        self.nodes = set()
    
    def createBlock(self, proof, previousHash):

        block = {
                'index': len(self.chain) + 1, # lito
                'transactions': self.transactions, # lito
                'timestamp': str(datetime.datetime.now()), # lito
                'proof': proof, # lito
                'previous_hash': previousHash, # lito
                'route': 'placeholder' #Puerto del node
                }
        ##Se deben vaciar las transacciones
        self.transactions = []
        
        self.chain.append(block)
        return block

    def getPreviousBlock(self):
        return self.chain[-1]

    def proofOfWork(self, previousProof):
        #Claves: Dificil de resolver - facil de verificar
        newProof = 1
        checkProof = False

        while checkProof is False:
            #No simétrico
            hashOperation = hashlib.sha224(str(newProof**2 - previousProof**2).encode()).hexdigest()

            if hashOperation[:2] == '00':#hashOperation[:8] == '00000000':
                checkProof = True
            else:
                newProof += 1

        return newProof

    def blockHash(self, block):
        encodeBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha224(encodeBlock).hexdigest()

    def isChainValid(self, chain):
        previousBlock = chain[0]
        blockIndex = 1

        while blockIndex < len(chain):
            block = chain[blockIndex]
            #Chequeo del hash previo
            if block['previous_hash'] != self.blockHash(previousBlock):
                return False
            
            #Validar proof
            previousProof = previousBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha224(str(proof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:2] != '00':#hashOperation[:8] != '00000000':
                return False

            #Iterar bloque
            previousBlock = block
            blockIndex +=1
        return True

    ##Agregar transacciones
    def addTransaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                'receiver': receiver,
                                'amount': amount})
        #Devolver el index del nuevo bloque
        previousBlock = self.getPreviousBlock()
        return previousBlock['index'] + 1

    ##Registrar nodos
    def addNode(self, address):
        #Parsear URL la segmenta
        parsedURL =urlparse(address)
        #Uso de netloc para extraer direccion y puerto (host and port)
        self.nodes.add(parsedURL.netloc)

    def deleteNode(self, address):
        #Parsear URL la segmenta
        parsedURL =urlparse(address)
        #Uso de netloc para extraer direccion y puerto (host and port)
        self.nodes.discard(parsedURL.netloc)


    ##Funcion de consenso
    def replaceChain(self):
        #Extraer red de nodos
        network = self.nodes
        longestChain = None
        maxLenght = len(self.chain)

        newerChain = None
        newerTime = datetime.datetime.strptime(self.block['datetime'],'%Y-%m-%d %H:%M:%S.%f')

        #Revisar la cadena mas larga en cada nodo
        for nodes in network:
            #Uso de requests para extraer la chain de cada nodo
            response = requests.get(f'http://{node}/getChain')
            if response.status_code == 200:
                lenght = response.json()['lenght']
                chain = response.json()['chain']

                #puede que nos de error
                time = datetime.datetime.strptime(response.json()['block']['datetime'],'%Y-%m-%d %H:%M:%S.%f')

                #Chequear largo y validez
                if lenght > maxLenght and self.isChainValid(chain):
                    maxLenght = lenght
                    longestChain = chain
        
                elif (lenght == maxLenght and self.isChainValid(chain)):
                    if (time > newerTime):
                        newerTime = time
                        newerChain = chain

        if longestChain or newerChain:
            self.chain = longestChain
            return True
        
        return False

    



#Crear aplicacion
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

##Crear dirección para nodo en puerto
nodeAddress = str(uuid4()).replace('-','')


#Instancia blockchain

blockchain = Blockchain()

#Minar bloques
@app.route('/mineBlock', methods=['GET'])
def mineBlock():
    #Obtener información de bloque previo
    previousBlock = blockchain.getPreviousBlock()
    previousProof = previousBlock['proof']
    previousHash = blockchain.blockHash(previousBlock)

    #Realizar proof of work
    proof = blockchain.proofOfWork(previousProof)

    ##Agregar transacciones
    blockchain.addTransaction(sender = nodeAddress, receiver = 'Yo', amount = 1000)

    #Crear bloque exitoso
    block = blockchain.createBlock(proof, previousHash)

    #Mensaje de respuesta ##Modificar transactions
    response = {'message':'Se ha minado un bloque',
                'index': block['index'],
                'transactions': block['transactions'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous hash':block['previous_hash']}

    #Retorno de respuesta
    return jsonify(response),200

#Obtener la blockchain

#REVISAR----

@app.route('/getChain', methods = ['GET'])
def getChain():
    infoBloques = ''
    bloque = blockchain.block

    for i in blockchain.chain:
        infoBloques += "index: {}, transaction: {}, timestamp: {}, proof: {}, previous hash: {}, route: {}\n".format(bloque['index'],bloque['transactions'],  bloque['timestamp'],  bloque['proof'],  bloque['previous_hash'],  bloque['route'])
        bloque = bloque.getPreviousBlock()

    response = {'chain':blockchain.chain,
                'block':blockchain.block,
                'blocks':infoBloques,
                'lenght of chain':len(blockchain.chain)}
    return jsonify(response),200

#Validar cadena
@app.route('/validateChain', methods = ['GET'])
def validateChain():
    response = {'Is valid': blockchain.isChainValid(blockchain.chain),
                'Date': blockchain.chain[-1]['timestamp']}
    return jsonify(response),200

@app.route('/CorruptChain', methods = ['POST'])
def CorruptChain():

    cadena = blockchain.chain
    bloque = cadena.block

    if (bloque['hash_bloque'][-1] != '1'):
        bloque['hash_bloque'] = bloque['hash_bloque'][:-1] + '1'
    
    else:
        bloque['hash_bloque'] = bloque['hash_bloque'][:-1] + '2'

    response = {'chain':cadena,
                'block':bloque,
                'lenght of chain':len(cadena)}
    return jsonify(response),200

##Agregar una nueva transaccion a la cadena
@app.route('/addTransaction', methods = ['POST'])
def addTransaction():
    json = request.get_json()
    #Verificar keys de transacciones
    transactionKeys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transactionKeys):
        return 'Algo me huele mal',400
    #Agregar al ultimo bloque
    index = blockchain.addTransaction(json['sender'], json['receiver'], json['amount'])

    response = {'message':f'Transaccion añadida al bloque {index}'}

    return jsonify(response),201    

##Descentralizar la red

##Conectar nodos nuevos
@app.route('/connectNode', methods = ['POST'])
def connectNode():
    json = request.get_json()
    nodes = json.get('nodes')
    #Chequear que hayan nodos
    if nodes is None:
        return 'No hay nada',400
    for node in nodes:
        blockchain.addNode(node)
    
    response = {'message':'Red de nodos actualizada',
                'total nodes':list(blockchain.nodes)}
    return jsonify(response),201

@app.route('/DisconnectNode', methods = ['GET'])
def DisconnectNode():
    json = request.get_json()
    nodes = json.get('nodes')
    #Chequear que hayan nodos
    if nodes is None:
        return 'No hay nada',400
    for node in nodes:
        blockchain.deleteNode(node)
    
    response = {'message':'Red de nodos actualizada',
                'total nodes':list(blockchain.nodes)}
    return jsonify(response),201

##Aplicar consenso y ver cual es la cadena mas larga - Actividad en clases

#REVISAR

@app.route('/ReplaceChain', methods = ['GET'])
def ReplaceChain():
    isChainReplaced = blockchain.replaceChain(blockchain.chain)
    if isChainReplaced:
        response = {'message':'Se ha reemplazado por una cadena mas larga',
                    'Nueva chain': blockchain.chain}
    else:
        response = {'message':'Tu blockchain es la cadena mas larga',
                    'Cadena actual': blockchain.chain}
    return jsonify(response),200


#Correr la aplicación
app.run(host = '0.0.0.0', port=5000)
##Node One - Nombre: Onnee, port:5001
##Node Two - Nombre: Towee, port:5002
##Node Three - Nombre: Turi, port:5003


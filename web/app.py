from flask_restful import Api, Resource
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bcrypt import hashpw, gensalt, checkpw

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')

db = client.BankAPI

users = db['Users']

def userExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True

def verfiyPw(username, password):
    if not userExist(username):
        return False
    
    hashedPw = users.find({
        "username": username
    })[0]['password']
    
    if checkpw(password, hashedPw):
        return True
    else:
        return False

def cashWithUser(username):
    return users.finnd({
        "username": username
    })[0]['own']

def debtWithUser(username):
    return users.finnd({
        "username": username
    })[0]['debt']

def generateReturnDictionary(status, message):
    return {
        "status": status,
        "message": message
    }

def verifyCredentials(username, password):
    if not userExist(username):
        return generateReturnDictionary(400, 'Invalid Username'), True
    
    correctPw = verfiyPw(username, password)
    if not correctPw:
        return generateReturnDictionary(400, 'Invalid Password'), True
    
    return None, False

def updateAccount(username, balance):
    users.update({
        "username": username
    }, {
        "$set": {
            "own": balance
        }
    })

def updateDebt(username, balance):
    users.update({
        "username": username
    }, {
        "$set": {
            "debt": balance
        }
    })

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData['username']
        password = postedData['password']
        
        if userExist(username):
            return  jsonify({
                "status": 400,
                "message": "Invalid User"
            })
            
        hashedPassword = hashpw(password.encode('utf8'), gensalt())
        
        users.insert({
            "username": username,
            "password": hashedPassword,
            "own": 0,
            "debt": 0
        })
        
        return jsonify({
            "status": 200,
            "message": "You have successfully signup for the API."
        })    

class Add(Resource):
    def post(self):
        postedData = request.add_json()

        username = postedData['username']
        password = postedData['password']
        money = postedData['amount']

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        if money <= 0:
            return jsonify(generateReturnDictionary(400, "The money amount entered must be > 0"))

        cash = cashWithUser(username)
        money -= 1
        bankCash = cashWithUser('BANK')
        updateAccount('BANK', bankCash + 1)
        updateAccount(username, cash + money)

        return jsonify(generateReturnDictionary(200, 'Amount added succesfully to account.'))

class Transfer(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData['username']
        password = postedData['password']
        to = postedData['to']
        money = postedData['amount']
        
        retJson, error = verifyCredentials(username, password)
        
        if error:
            return jsonify(retJson)
        
        cash = cashWithUser(username)
        if cash <= 0:
            return jsonify(generateReturnDictionary(400, 'You are out of money, please deposit money to your account.'))
        
        if not username(to):
            return jsonify(generateReturnDictionary(400, 'User name is invalid.'))
        
        cash_from = cashWithUser(username)
        cash_to = cashWithUser(to)
        bank_cash = cashWithUser('BANK')
        
        updateAccount('BANK', bank_cash + 1)
        updateAccount(to, cash_to + money - 1)
        updateAccount(userExist, cash_from - money)
        
        return jsonify(generateReturnDictionary(200, 'Amount transfered successfully'))

class Balance(Resource):
    def get(self):
        postedData = request.get_json()
        
        username = postedData['username']
        password = postedData['password']
        
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        
        return jsonify(users.find({
            "username": username
        }, {
            "password": 0,
            "_id": 0
        })[0])

class TakeLoan(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData['username']
        password = postedData['password']
        money = postedData['amount']
        
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
            
        cash = cashWithUser(username)
        debt = debtWithUser(username)

        updateAccount(username, cash + money)
        updateDebt(username, debt + money)
        
        return jsonify(generateReturnDictionary(200, 'Loan added to your account'))

class PayLoan(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['password']
        money = postedData['amount']
        
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        
        cash = cashWithUser(username)
        if cash < money:
            return jsonify(400, 'Not enough money in your account')
            
        debt = debtWithUser(username)

        updateAccount(username, cash - money)
        updateDebt(username, debt - money)
        
        return jsonify(generateReturnDictionary(200, 'You have successfully paid on your loan'))
        
        
api.add_resource(Register, '/register')
api.add_resource(Add, '/add')
api.add_resource(Transfer, '/transfer')
api.add_resource(Balance, '/balance')
api.add_resource(TakeLoan, '/takeloan')
api.add_resource(PayLoan, '/payloan')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
from urllib import parse
from flask import Flask, request
import pymongo
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from util import *
from bson.objectid import ObjectId

client = MongoClient('mongodb+srv://:@cluster0.47fza.mongodb.net/decathlon?retryWrites=true&w=majority')

users = client.decathlon.users
leaves = client.decathlon.leaves
passwords = client.decathlon.passwords
metrics = client.decathlon.metrics
 
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/login', methods = ['GET'])
@cross_origin()
def validateLogin():
    headerdict = dict(request.headers)
    empId = headerdict['Empid']
    pwd = headerdict['Pwd']
    response = passwords.find_one({"empId": empId, "pass": pwd})
    if response is None:
        return createJsonResponse(False)
    else:
        return getEmployee(empId)

@app.route('/employee/<empId>', methods = ['GET'])
@cross_origin()
def getEmployee(empId):
    inputStr = str(empId)
    if inputStr[:3] != "emp":
        inputStr = "emp" + inputStr
    employee = getUserData(inputStr)
    return createJsonResponse(employee)

@app.route('/employee/count', methods=['GET'])
@cross_origin()
def getEmployeeCount():
    empCount = empCountData()
    return createJsonResponse(empCount)

@app.route('/employee/add', methods=['POST'])
@cross_origin()
def addEmployee():
    body = request.data.decode()
    bodyJson = json.loads(parse_json(body))
    count = empCountData()['count']
    newCount = count + 1
    try:
        bodyJson['empId'] = "emp" + str(count+1)
        bodyJson['isHr'] = False
        users.insert_one(bodyJson)
        passwords.insert_one({"empId": bodyJson['empId'], "pass": "123"})
        metrics.find_one_and_update({"metric": "empCount"}, { '$set': {"count": newCount}})
        return {"response": bodyJson['empId']}
    except:
        return {}

@app.route('/employee/modify', methods=['PUT'])
@cross_origin()
def modifyEmployee():
    body = request.data.decode()
    bodyJson = json.loads(parse_json(body))
    try:
        users.find_one_and_update({"empId": str(bodyJson["empId"])}, { '$set': bodyJson})
    except:
        return {}
    return {"response" :True}

@app.route('/leaves/<empId>', methods = ['GET'])
@cross_origin()
def getLeavesForEmployee(empId):
    leaveData =  getLeaveData(empId)
    return createJsonResponse(leaveData)

@app.route('/leaves/pending', methods = ['GET'])
@cross_origin()
def getAllPendingLeaves():
    leaveData =  getPendingLeaveData()
    return createJsonResponse(leaveData)

@app.route('/leaves/add', methods = ['POST'])
@cross_origin()
def postNewLeave():
    body = request.data.decode()
    bodyJson = json.loads(parse_json(body))
    try:
        leaves.insert_one(bodyJson)
    except:
        return {}
    return {"response" : True}

@app.route('/leaves/modify', methods=['GET','POST', 'PUT'])
@cross_origin()
def modifyLeave():
    body = request.data.decode()
    bodyJson = json.loads(parse_json(body))
    id = str(bodyJson['id']["$oid"])
    try:
        leaves.find_one_and_update({"_id": ObjectId(id)}, { '$set': {"status": bodyJson['status']}})
    except:
        return {}
    return {"response" : True}

def getUserData(empId):
    return users.find_one({"empId": empId})

def getLeaveData(empId):
    return leaves.find({"empId": empId}).sort('from', pymongo.DESCENDING)

def getPendingLeaveData():
    return leaves.find({"status": "Pending"}).sort('from', pymongo.DESCENDING)

def empCountData():
    return metrics.find_one({"metric": "empCount"})
 
if __name__ == '__main__':
    app.run(debug=True)

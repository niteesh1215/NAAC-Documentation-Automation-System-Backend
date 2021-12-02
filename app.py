from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import default, dumps
import json
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import response_message
import schedule
import time
from datetime import date
from flask_cors import CORS

baseUrl = "/api/v1"

app = Flask(__name__)

CORS(app)

app.secret_key = "blinsia"
app.config['MONGO_URI'] = "mongodb+srv://spm:spm@spm.hcqrx.mongodb.net/SPM?retryWrites=true&w=majority"
#app.config['MONGO_URI'] = "mongodb://127.0.0.1:27017/spm"
mongo = PyMongo(app)
# mongodb+srv://spm:spm@spm.hcqrx.mongodb.net/SPM?retryWrites=true&w=majority
# mongodb://localhost:27017/spm


@app.route("/")
def index():
    return "Welcome to NAAC Documentation Automation System"

# register and login start ###################################################################################


@app.route(baseUrl+"/auth/register", methods=["POST"])
def register_user():
    try:
        _json = request.json
        _name = _json["name"]
        _email = _json["email"]
        _pwd = _json['pwd']

        if _name and _email and _pwd and request.method == "POST":
            _hashed_pwd = generate_password_hash(_pwd)
            result = mongo.db.user.insert_one(
                {'name': _name, 'email': _email, 'pwd': _hashed_pwd})

            return response_message.get_success_response("Inserted suceessfully")
        else:
            return response_message.get_failed_response("Insertion failed, please provide correct data")
    except Exception as e:
        error_message = str(e)
        if(error_message.find('duplicate key') != -1):
            return response_message.get_failed_response("Email id exists")
        else:
            return response_message.get_failed_response("An error occured")


@app.route(baseUrl+"/auth/login", methods=["POST"])
def login_user():
    try:
        _json = request.json
        _email = _json["email"]
        _pwd = _json['pwd']
        if _email and _pwd and request.method == "POST":

            result = mongo.db.user.find_one(
                {"email": _email})

            doc = json.loads(dumps(result))

            if check_password_hash(doc['pwd'], _pwd):
                return response_message.get_success_response("Log in success")
            else:
                return response_message.get_failed_response("Log in failed")

        else:
            return response_message.get_failed_response("Failed, please provide correct data")
    except Exception as e:
        print(e)
        return response_message.get_failed_response("An error occured")

# register and login End ###################################################################################

# files Start #################################################################################


@app.route(baseUrl+"/files/create-file", methods=["PUT"])
def createfile():
    try:
        _json = request.json
        _name = _json["name"]
        _path = _json["path"]
        _description = _json["description"]
        _type = _json["type"]
        _createdOn = _json["createdOn"]
        _formDetails = None
        if "formDetails" in _json:
            _formDetails = _json["formDetails"]

        if _type == "FORM":
            if _formDetails:
                try:
                    formId = mongo.db.forms.insert_one(_formDetails)
                    convertedFormId = json.loads(
                        dumps(formId.inserted_id))['$oid']
                    if _name and _path and _description and _type and _createdOn and formId and request.method == "PUT":
                        mongo.db.files.insert_one(
                            {"name": _name, "path": _path, "description": _description, "type": _type, "createdOn": _createdOn, "formId": convertedFormId})
                        return response_message.get_success_response("Form inserted suceessfully")
                except:
                    mongo.db.forms.delete_one({"_id": formId})
                    return response_message.get_failed_response("Error while inserting form")
            else:
                return response_message.get_failed_response("Failed in inserting form")

        if _name and _path and _description and _type and _createdOn and request.method == "PUT":

            mongo.db.files.insert_one(
                {"name": _name, "path": _path, "description": _description, "type": _type, "createdOn": _createdOn})
            return response_message.get_success_response("Inserted in files suceessfully")
        else:
            return response_message.get_failed_response("Failed in inserting file")
    except Exception as e:
        print(e)
        return response_message.get_failed_response("An error occured")


@app.route(baseUrl+"/files/edit-file", methods=["PUT"])
def editfile():
    try:
        _json = request.json
        _fileId = _json["id"]
        _editData = _json["editData"]

        if _fileId and _editData and request.method == "PUT":
            result = mongo.db.files.update_one(
                {"_id": ObjectId(_fileId)}, {"$set": _editData})
            return response_message.get_success_response("Updated suceessfully")
        else:
            return response_message.get_failed_response("Failed")
    except Exception as e:
        print(e)
        return response_message.get_failed_response("An error occured")


@app.route(baseUrl+"/files/delete-file/<id>", methods=["DELETE"])
def deletefile(id):
    try:

        if id and request.method == "DELETE":
            result = mongo.db.files.find_one({"_id": ObjectId(id)})
            mongo.db.files.delete_one({"_id": ObjectId(id)})
            mongo.db.forms.delete_one({'_id': ObjectId(result['formId'])})
            return response_message.get_success_response("Deleted suceessfully")
        else:
            return response_message.get_failed_response("Failed")
    except Exception as e:
        print(e)
        return response_message.get_failed_response("An error occured")


@app.route(baseUrl+"/files/retrieve", methods=["POST"])
def retrieve():
    try:
        _json = request.json
        _path = _json["path"]

        if _path and request.method == "POST":
            result = mongo.db.files.find({"path": _path})

            return response_message.get_success_response(json.loads(dumps(result)))
        else:
            return response_message.get_failed_response("Failed")
    except Exception as e:
        print(e)
        return response_message.get_failed_response("An error occured")

# files End #################################################################################


@app.route(baseUrl+"/form/response/add", methods=["POST"])
def user_response():
    try:
        _json = request.json
        _submittedOn = _json['submittedOn']
        _formId = _json['formId']
        _email = _json['email']
        _responseData = _json['responseData']
        _responseGroupId = _json['responseGroupId']
        if _submittedOn and _formId and _email and _responseData and _responseGroupId and request.method == "POST":
            result = mongo.db.responses.insert_one(
                {'submittedOn': _submittedOn, 'formId': _formId, 'email': _email, 'responseData': _responseData, 'responseGroupId': _responseGroupId})

            return response_message.get_success_response("Inserted successfully")
        else:
            return response_message.get_failed_response("Insertion failed, please provide correct data")
    except Exception as e:
        error_message = str(e)
        if(error_message.find('duplicate key') != -1):
            return response_message.get_failed_response("Email id exists")
        else:
            return response_message.get_failed_response("An error occured")


@app.route(baseUrl+"/form/response/retrieve", methods=["GET"])
def retrieve_response():
    try:

        _json = request.json
        _formId = _json['formId']
        _responseGroupId = _json['responseGroupId']
        if _formId and _responseGroupId and request.method == "GET":
            form = mongo.db.responses.find(
                {'formId': _formId, 'responseGroupId': _responseGroupId})
            return response_message.get_success_response(json.loads(dumps(form)))
        elif _formId and request.method == "GET":
            form = mongo.db.responses.find({'formId': _formId})
            return response_message.get_success_response(json.loads(dumps(form)))
        elif _responseGroupId and request.method == "GET":
            form = mongo.db.responses.find(
                {'responseGroupId': _responseGroupId})
            return response_message.get_success_response(json.loads(dumps(form)))
        else:
            return response_message.get_failed_response("An error occured ")
    except Exception as e:
        error_message = str(e)
        return response_message.get_failed_response("An error occured "+error_message)


@app.route(baseUrl+"/form/response/delete/<id>", methods=["DELETE"])
def delete_user_response(id):
    try:
        mongo.db.responses.delete_one({'_id': ObjectId(id)})
        return response_message.get_success_response("Deleted successfully")
    except Exception as e:
        error_message = str(e)
        return response_message.get_failed_response("An error occured "+error_message)


@app.route(baseUrl+"/form/response/update-response-data/<id>", methods=["PUT"])
def update_response_data(id):
    try:
        _json = request.json
        _id = id
        _responseData = _json['responseData']

        if _id and _responseData and request.method == 'PUT':
            mongo.db.responses.update_one({'_id': ObjectId(_id['$oid']) if'$oid' in _id else ObjectId(
                _id)._}, {'$set': {'response_data': _responseData}})
            return response_message.get_success_response("Updated successfully")
    except Exception as e:
        error_message = str(e)
        return response_message.get_failed_response("An error occured "+error_message)

# form responses ###################################################################################


@app.route(baseUrl+"/form/add", methods=["POST"])
def add_form():
    try:
        _json = request.json
        _name = _json['name']
        _description = _json['description']
        _template = _json['template']
        _path = _json['path']
        _limitToSingleResponse = _json['limitToSingleResponse']
        _currentGroupId = _json['currentGroupId']
        if _name and _description and _template and _path and _limitToSingleResponse and _currentGroupId and request.method == "POST":
            result = mongo.db.forms.insert_one(
                {'name': _name, 'description': _description, 'template': _template, 'path': _path, 'limitToSingleResponse': _limitToSingleResponse, 'currentGroupId': _currentGroupId, 'createdOn': None, 'isActive': False, 'activeFromDate': None, 'activeEndDate': None, 'lastModified': None})

            print(result.__doc__)

            return response_message.get_success_response("Inserted successfully")
        else:
            return response_message.get_failed_response("Insertion failed, please provide correct data")
    except Exception as e:
        error_message = str(e)
        if(error_message.find('duplicate key') != -1):
            return response_message.get_failed_response("Email id exists")
        else:
            return response_message.get_failed_response("An error occured")


@app.route(baseUrl+"/form/update/<id>", methods=["PUT"])
def update_form(id):
    try:
        _json = request.json
        _json.pop('_id')

        if id and request.method == 'PUT':
            mongo.db.forms.update_one({'_id': ObjectId(id['$oid']) if'$oid' in id else ObjectId(
                id)}, {'$set': request.json})

            mongo.db.files.update_one({"formId": id['$oid'] if'$oid' in id else
                                       id}, {"$set": {
                                           'name': _json['name'],
                                           'description': _json['description'],
                                       }})
            return response_message.get_success_response("Updated successfully")

    except Exception as e:
        error_message = str(e)
        return response_message.get_failed_response("An error occured "+error_message)


@app.route(baseUrl+"/form/retrieve/<id>", methods=["GET"])
def retrieve_form(id):
    try:
        _formId = id
        if _formId and request.method == "GET":
            form = mongo.db.forms.find_one({'_id': ObjectId(_formId)})
            return response_message.get_success_response(json.loads(dumps(form)))

    except Exception as e:
        error_message = str(e)
        return response_message.get_failed_response("An error occured "+error_message)


@app.route(baseUrl+"/form/retrieve-active", methods=["GET"])
def retrieve_active_form():
    try:
        form = mongo.db.forms.find({'isActive': True})
        return response_message.get_success_response(json.loads(dumps(form)))

    except Exception as e:
        error_message = str(e)
        return response_message.get_failed_response("An error occured "+error_message)

# forms ###################################################################################


@app.route(baseUrl+"/form/add-test", methods=["PUT"])
def add_test():
    def job():

        _today = str(date.today())
        print(_today)
        mongo.db.forms.update_one({'activeEndDate': _today}, {
                                  "$set": {'isActive': False}})
        return response_message.get_success_response("Updated successfully")

    schedule.every().day.at("22:33").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


@app.errorhandler(404)
def not_found(error=None):
    return response_message.get_failed_response("Not found" + request.url, status_code=404)


if __name__ == "__main__":
    app.run(debug=True)

import re
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import default, dumps
import json
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import response_message

baseUrl = "/api/v1"

app = Flask(__name__)

app.secret_key = "blinsia"
# app.config['MONGO_URI'] = "mongodb+srv://spm:spm@spm.hcqrx.mongodb.net/SPM?retryWrites=true&w=majority"
app.config['MONGO_URI'] = "mongodb://127.0.0.1:27017/spm"
mongo = PyMongo(app)


@app.route("/")
def index():
    return "Welcome to NAAC Documentation Automation System"

# register and login ###################################################################################


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

# register and login ###################################################################################


@app.route(baseUrl+"/form/response/add", methods=["POST"])
def user_response():
    try:
        _json = request.json
        _submittedOn = _json['submittedOn']
        _form_id = _json['form_id']
        _email = _json['email']
        _response_data = _json['response_data']
        _response_group_id = _json['response_group_id']
        if _submittedOn and _form_id and _email and _response_data and _response_group_id and request.method == "POST":
            result = mongo.db.responses.insert_one(
                {'submittedOn': _submittedOn, 'form_id': _form_id, 'email': _email, 'response_data': _response_data, 'response_group_id': _response_group_id})

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
        _response_data = _json['response_data']

        if _id and _response_data and request.method == 'PUT':
            mongo.db.responses.update_one({'_id': ObjectId(_id['$oid']) if'$oid' in _id else ObjectId(
                _id)}, {'$set': {'response_data': _response_data}})
            return response_message.get_success_response("Updated successfully")
    except Exception as e:
        error_message = str(e)
        return response_message.get_failed_response("An error occured "+error_message)


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
                {'name': _name, 'description': _description, 'template': _template, 'path': _path, 'limitToSingleResponse': _limitToSingleResponse, 'currentGroupId': _currentGroupId, 'createdOn': None, 'isActive': None, 'activeFromDate': None, 'activeEndDate': None, 'lastModified': None})

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


@app.errorhandler(404)
def not_found(error=None):
    return response_message.get_failed_response("Not found" + request.url, status_code=404)


if __name__ == "__main__":
    app.run(debug=True)

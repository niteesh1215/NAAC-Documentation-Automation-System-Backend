from flask import Flask, jsonify, request
from flask_pymongo import ASCENDING, PyMongo
from bson.json_util import default, dumps
import json
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import response_message
from datetime import datetime


baseUrl = "/api/v1"

app = Flask(__name__)

app.secret_key = "blinsia"
app.config['MONGO_URI'] = "mongodb+srv://spm:spm@spm.hcqrx.mongodb.net/SPM?retryWrites=true&w=majority"
mongo = PyMongo(app)
#mongodb+srv://spm:spm@spm.hcqrx.mongodb.net/SPM?retryWrites=true&w=majority
#mongodb://localhost:27017/spm

@app.route("/")
def index():
    return "Welcome to NAAC Documentation Automation System"

# register and login start ###################################################################################
@app.route(baseUrl+"/auth/register/", methods=["POST"])
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
        _createdOn = datetime.now()
        #_formdetails = _json["formdetails"]

        if _name and _path and _description and _type and _createdOn and request.method == "PUT":
            result = mongo.db.files.insert_one(
                {"name":_name,"path":_path,"description":_description,"type":_type,"createdOn":_createdOn})
            return response_message.get_success_response("Inserted suceessfully")
        else:
            return response_message.get_failed_response("Failed")
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
            result = mongo.db.files.update({"_id":ObjectId(_fileId)},{"$set":_editData})
            return response_message.get_success_response("Updated suceessfully")
        else:
            return response_message.get_failed_response("Failed")
    except Exception as e:
        print(e)
        return response_message.get_failed_response("An error occured")


@app.route(baseUrl+"/files/delete-file", methods=["DELETE"])
def deletefile():
    try:
        _json = request.json
        _fileId = _json["id"]

        if _fileId and request.method == "DELETE":
            result = mongo.db.files.delete_one({"_id":ObjectId(_fileId)})
            
            return response_message.get_success_response("Deleted suceessfully")
        else:
            return response_message.get_failed_response("Failed")
    except Exception as e:
        print(e)
        return response_message.get_failed_response("An error occured")


# files End ################################################################################# 

@app.errorhandler(404)
def not_found(error=None):
    return response_message.get_failed_response("Not found" + request.url, status_code=404)


if __name__ == "__main__":
    app.run(debug=True)

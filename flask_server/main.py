import sys, os
from flask import Flask, request, jsonify
import config
from database.db_connect import db
from database import module
from flask_restx import Resource, Api

app = Flask(__name__) # app assignment
app.config.from_object(config) # app setting config through config object(related to DB)
db.init_app(app)
api = Api(app) # api that make restapi more easier

@api.route('/test/<string:uuid>')
class test(Resource):
    def get(self, uuid):
        return module.user_info_table.query.filter_by(user_uuid=uuid).first().git_nickname
    def post(self, uuid):
        data = request.get_json()
        return jsonify(data)

@app.route('/')
def main_page_mesg():
    return "this is capstone main page\n"

@api.route('/interest_list/<string:uuid>')
class interest_list(Resource):
    def get(self, uuid): 
         raw_interest_list = module.User.query.filter_by(user_uuid=uuid).first().interesting_field
         #raw_interest_list = "ab,cd,ef,gh" #test code
         interest_list = raw_interest_list.split(',')
         return interest_list
    def put(self, uuid):
        interest_list = request.get_json()['interest_list']
        #interest_list = ['i1', 'i2', 'i3', 'i4', 'i5'] # testcode
        processed_list = ""
        for interest_subject in interest_list:
            processed_list += interest_subject + ','
        processed_list = processed_list[0:-1]
        try:
            user = module.User.query.filter_by(user_uuid=uuid).first()
            user.interesting_field = processed_list
            db.session.commit()
        except:
            return 0
        return 1

if __name__ == "__main__":
    app.run(host = "0.0.0.0")

from flask import Blueprint, request, jsonify
from flask_restx import Resource, Api
from database.db_connect import db
from database import module

user_ab = Blueprint('user', __name__)
api = Api(user_ab) # api that make restapi more easier

@api.route('/interesting_field/<string:uuid>')
class interest_list(Resource):
    def get(self, uuid): 
         raw_interest_list = module.User.query.filter_by(user_uuid=uuid).first().interesting_field
         #raw_interest_list = "ab,cd,ef,gh" #test code
         interest_list = raw_interest_list.split(',')
         return interest_list
    def put(self, uuid):
        interest_list = request.get_json()['interesting_field']
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
    def delete(self, uuid):
        try:
            user = module.User.query.filter_by(user_uuid=uuid).first()
            user.interesting_field = ""
            db.session.commit()
        except:
            return 0
        return 1


@user_ab.route('/test')
def test():
    raw_interest_list = module.User.query.filter_by(interesting_field="java,c++,c").all()
    print(raw_interest_list[0].user_uuid)
    return "0"



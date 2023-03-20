from flask import Blueprint, request, jsonify, make_response
from flask_restx import Resource, Api
from database.db_connect import db
from database import module
from datetime import datetime
import pytz

user_ab = Blueprint('user', __name__)
api = Api(user_ab) # api that make restapi more easier

def turn_datetime_to_longint(dt):
    ret = dt.year
    ret = 100*ret + dt.month
    ret = 100*ret + dt.day
    ret = 100*ret + dt.hour
    ret = 100*ret + dt.minute
    return ret

@api.route('/date')
class date(Resource):
    def get(self):
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        ret = turn_datetime_to_longint(now)
        return ret

@api.route('/attendance/<string:uuid>')
class attendance(Resource):
    def post(self, uuid):
        new_attd = module.Attendance()

default_interest_list = ['os', 'database', 'server', 'c++', 'java', 'python']

@api.route('/interesting_field/<string:uuid>')
class interest_list(Resource):
    def get(self, uuid):
         raw_interest_list = module.User.query.filter_by(user_uuid=uuid).first().interesting_field
         #raw_interest_list = "ab,cd,ef,gh" #test code
         interest_list = raw_interest_list.split(',')
         ret = []

         for subject in default_interest_list:
            if subject in interest_list:
                ret.append({"selected":True, "field_name":subject})
            else:
                ret.append({"selected":False, "field_name":subject})
         return jsonify(ret)
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

        try:
            user = module.User.query.filter_by(user_uuid=uuid).first()
            user.interesting_field = ""
            db.session.commit()
        except:
            return 0
        return 1

@api.route('attendance/<string:uuid>')
class attendance(Resource):
    def get(self, uuid):
        raw_interest_list = module.User.query.filter_by(user_uuid=uuid).first().interesting_field



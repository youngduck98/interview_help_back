from flask import Blueprint, request, jsonify, make_response
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommandation, CommunityComment
from datetime import datetime, timedelta, date, time, timezone
import pytz
import uuid

user_ab = Blueprint('user', __name__)
api = Api(user_ab) # api that make restapi more easier

def turn_datetime_to_longint(dt):
    ret = dt.year
    ret = 100*ret + dt.month
    ret = 100*ret + dt.day
    ret = 100*ret + dt.hour
    ret = 100*ret + dt.minute
    return ret

def yesterday_return(today):
    d = today.date()
    t = time(0,0)
    toDate = datetime.combine(d, t)
    fromDate = toDate - timedelta(days=1)
    
    return fromDate, toDate

def today_return(today):
    d = today.date()
    t = time(0,0)
    fromDate = datetime.combine(d, t)
    toDate = fromDate + timedelta(days=1)
    
    return fromDate, toDate


@api.route('/date/<string:uuid2>')
class date(Resource):
    def get(self, uuid2):
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        fromdate, todate = yesterday_return(now)
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        if(user_record):
            return 1
        return 0
        ret1 = turn_datetime_to_longint(fromdate)
        ret2 = turn_datetime_to_longint(todate)
        return ret2

#def __init__(self, att_uuid, user_uuid, att_date = datetime.now(pytz.timezone('Asia/Seoul'))):
@api.route('/attendance/<string:uuid2>')
class attendance(Resource):
    def get(self, uuid2):
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        fromdate, todate = today_return(today)
        #check user_uuid is exist
        try:
            target_user = User.query.get(uuid2)
        except:
            return -1
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        if(user_record):
            return 1
        return 0
    def post(self, uuid2):
        new_att_uuid = uuid.uuid1()
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        fromdate, todate = yesterday_return(today)
        try:
            target_user = User.query.get(uuid2)
        except:
            return 0
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        fromdate, todate = today_return(today)
        user_record2 = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        if(user_record and not user_record2):
            target_user.att_continue+=1
        else:
            target_user.att_continue=1
        try:
            new_attd = Attendance(new_att_uuid, uuid2)
            db.session.add(new_attd)
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, uuid2):
        print(2)
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        fromdate, todate = today_return(today)
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        target_user = User.query.filter(User.user_uuid == uuid2).first()
        if(user_record):
            db.session.delete(user_record)
            if(target_user.att_continue > 0):
                target_user.att_continue -= 1
            db.session.commit()
            return 1
        else:
            return 0
        
        
        
        
        
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

@api.route('attendance/<string:uuid>')
class attendance(Resource):
    def get(self, uuid):
        raw_interest_list = module.User.query.filter_by(user_uuid=uuid).first().interesting_field



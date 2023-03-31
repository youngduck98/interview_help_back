from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.expression import func
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommandation, CommunityComment
from database.list import default_interest_list
from database.dictionary import ques_type_dict
from datetime import datetime, timedelta, date, time, timezone
import pytz, uuid, json

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

def week_return(today, weekday):
    d = today.date()
    t = time(0,0)
    fromDate = datetime.combine(d,t) - timedelta(days = weekday)
    toDate = fromDate + timedelta(days=7)
    
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

@api.route('/cont_attendance/')
class cont_attendacne(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        print(user_uuid)
        target_user = User.query.get(user_uuid)
        if(target_user):
            days = target_user.att_continue
            return days
        return 0
    def put(self):
        user_uuid = request.args.get('user_uuid')
        days = request.args.get('days')
        target_user = User.query.get(user_uuid)
        if(target_user):
            target_user.att_continue = days
            try:
                db.session.commit()
            except:
                return -1
            return 1
        else:
            return 0

#def __init__(self, att_uuid, user_uuid, att_date = datetime.now(pytz.timezone('Asia/Seoul'))):
@api.route('/week_attendance/<string:user_uuid>')
class week_attendance(Resource):
    def get(self, user_uuid):
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        weekday = today.weekday()
        fromdate, todate = week_return(today, weekday)
        target_user = User.query.get(user_uuid)
        if(not target_user):
            return 0
        
        att_record = Attendance.query.filter(Attendance.user_uuid == user_uuid, \
            Attendance.att_date > fromdate, Attendance.att_date<todate).all()
        
        week_att = [0,0,0,0,0,0,0]
        for day in att_record:
            week_att[day.att_date.weekday()] = 1
        week_att = week_att[0:today.weekday()]
        return week_att             
        
#today_question/?user_uuid=<string>&current_ques_uuid=<string>
"""
1. it will be more sensible, set a category advance before ask to backend
2. this will reduce a lot of code
"""
@api.route('/today_question/')
class today_question(Resource):
    def get(self):
        category = request.args.get('category')
        category = ques_type_dict[category]
        current_ques_uuid = request.args.get('current_ques_uuid')
        que_record = db.session.query(CommonQue).filter(CommonQue.ques_uuid != current_ques_uuid, CommonQue.ques_type == category).\
            order_by(func.random()).all()
        if(que_record):
            return json.dumps({"ques_uuid":que_record})
        return 0

#def __init__(self, tq_uuid, user_uuid, today_ques, user_memo="", date=)
@api.route('/common_ques_memo/')
class commmon_ques_memo(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.tq_uuid == common_ques_uuid,\
            TodayQue.user_uuid == user_uuid).first()
        question = db.session.query(CommonQue.ques_uuid, CommonQue.question).\
            filter(CommonQue.ques_uuid == record.today_ques).first()
        if(record):
            dt = turn_datetime_to_longint(record.date)
            return jsonify({"question_uuid":question.ques_uuid, "question":question.question,\
                "memo":record.user_memo, "saved_date":dt})
        return 0
    def put(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.tq_uuid == common_ques_uuid,\
            TodayQue.user_uuid == user_uuid).first()
        try:
            record.user_memo = request.args.get('memo')
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.tq_uuid == common_ques_uuid,\
            TodayQue.user_uuid == user_uuid).first()
        try:
            record.user_memo = ""
            db.session.commit()
        except:
            return 0
        return 1
#def __init__(self, user_uuid, git_nickname, interesting_field, name, email, att_continue=0)
@api.route('/interesting_field/<string:uuid>')
class interest_list(Resource):
    def get(self, uuid):
         raw_interest_list = User.query.filter_by(user_uuid=uuid).first().interesting_field
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
            user = User.query.filter_by(user_uuid=uuid).first()
            user.interesting_field = processed_list
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, uuid):
        try:
            user = User.query.filter_by(user_uuid=uuid).first()
            user.interesting_field = ""
            db.session.commit()
        except:
            return 0
        return 1

#def __init__(self, script_uuid, script_host, script_date, script_title, question=""):
#def __init__(self, script_ques_uuid, question, index=0, tip=""): - Q
@api.route('/self_intro_script/')
class self_intro_script(Resource):
    def get(self):
        script_uuid = request.args.get('script_uuid')
        user_uuid = request.args.get('user_uuid')
        record = db.session.query(SynthesisSelfIntroduction).filter(\
            SynthesisSelfIntroduction.script_uuid==script_uuid, \
                SynthesisSelfIntroduction.script_host == user_uuid).first()
        date = turn_datetime_to_longint(record.script_date)
        que_uuid_list = record.question.split(',')
        que_list = []
        for que_uuid in que_uuid_list:
            que_record = db.session.query(SelfIntroductionQ).filter(\
                SelfIntroductionQ.script_ques_uuid == que_uuid).first()
            que_list.append(jsonify({"script_item_uuid":que_record.script_ques_uuid,\
                "question":que_record.question, "index":que_record.index}))
        #작성중
        

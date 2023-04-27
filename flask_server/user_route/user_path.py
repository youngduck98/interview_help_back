from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.expression import func
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommendation, CommunityComment
from database.list import default_interest_list
from database.dictionary import ques_type_dict
from function.about_time import date_return, turn_datetime_to_longint
from datetime import datetime, timedelta, date, time, timezone
import pytz, uuid, json, random
from github import Github

user_ab = Blueprint('user', __name__)
api = Api(user_ab) # api that make restapi more easier

@api.route('/git_lang/<string:uuid2>')
class git_lang(Resource):
    def get(self, uuid2):
        g = Github("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")
        git_nickname = User.query.get(uuid2)
        if(not git_nickname):
            return None
        
        try:
            user = g.get_user(git_nickname)
            user = g.get_user("youngduck98")#test code
        except:
            return "fail to get git_nickname"
        
        languages = []
        
        for repo in user.get_repos():
            # Get the programming languages used in this repository
            repo_languages = repo.get_languages()
            # Append the programming languages to the list of languages used by the user
            for language in repo_languages:
                if language not in languages:
                    languages.append({language: })
        
        

@api.route('/date/<string:uuid2>')
class date(Resource):
    def get(self, uuid2):
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        fromdate, todate = date_return(now, -1)
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        if(user_record):
            return 1
        ret1 = turn_datetime_to_longint(fromdate)
        ret2 = turn_datetime_to_longint(todate)
        return jsonify({"from":ret1,"to": ret2})

#def __init__(self, att_uuid, user_uuid, att_date = datetime.now(pytz.timezone('Asia/Seoul'))):
@api.route('/today_attendance/<string:uuid2>')
class attendance(Resource):
    def get(self, uuid2):
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        fromdate, todate = date_return(today, 0)
        #check user_uuid is exist
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        if(user_record):
            return 1
        return 0
    def post(self, uuid2):
        new_att_uuid = uuid.uuid1()
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        fromdate, todate = date_return(today, -1)
        try:
            target_user = User.query.get(uuid2)
        except:
            return 0
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date < todate).first()
        fromdate, todate = date_return(today, 0)
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
        fromdate, todate = date_return(today, 0)
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
        fromdate, todate = date_return(today, -1 * weekday, 7)
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

@api.route('/change_today_question/')
class change_today_question(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        raw_interest_list = db.session.query(User).filter(User.user_uuid==user_uuid).first().interesting_field
        interest_list = raw_interest_list.split(',')
        category = ques_type_dict[interest_list[random.randint(0, len(interest_list)-1)]]
        current_ques_uuid = request.args.get('current_ques_uuid')
        que_record = db.session.query(CommonQue).filter(CommonQue.ques_uuid != current_ques_uuid, CommonQue.ques_type == category).\
            order_by(func.random()).first()
        if(que_record):
            return jsonify({"ques_uuid":que_record.ques_uuid, "question": que_record.question})
        return 0

@api.route('/first_today_question/')
class first_today_question(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        record = db.session.query(User).filter(User.user_uuid==user_uuid).first()
        if(not record):
            return None
        raw_interest_list = record.interesting_field
        interest_list = raw_interest_list.split(',')
        print(ques_type_dict["java"])
        category = ques_type_dict[interest_list[random.randint(0, len(interest_list)-1)]]
        que_record = db.session.query(CommonQue).filter(CommonQue.ques_type == category).\
            order_by(func.random()).first()
        if(que_record):
            return jsonify({"ques_uuid":que_record.ques_uuid, "question": que_record.question})
        que_record = db.session.query(CommonQue).order_by(func.random()).first()
        return jsonify({"ques_uuid":que_record.ques_uuid, "question": que_record.question})
#def __init__(self, tq_uuid, user_uuid, today_ques, user_memo="", date=)
@api.route('/common_ques_memo/')
class commmon_ques_memo(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.tq_uuid == common_ques_uuid,\
            TodayQue.user_uuid == user_uuid).first()
        if(record):
            question = db.session.query(CommonQue.ques_uuid, CommonQue.question).\
                filter(CommonQue.ques_uuid == record.today_ques).first()
            dt = turn_datetime_to_longint(record.date)
            return jsonify({"question_uuid":question.ques_uuid, "question":question.question,\
                "memo":record.user_memo, "saved_date":dt})
        return None
    def post(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        user_memo = request.get_json()['memo']
        tq_uuid = uuid.uuid1()
        date = datetime.now(pytz.timezone('Asia/Seoul'))
        today_que_record = TodayQue(tq_uuid, user_uuid, common_ques_uuid,\
            user_memo, date)
        db.session.add(today_que_record)
        db.session.commit()
    def put(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.tq_uuid == common_ques_uuid,\
            TodayQue.user_uuid == user_uuid).first()
        try:
            record.user_memo = request.get_json()['memo']
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

# def __init__(self, tq_uuid, user_uuid, today_ques, user_memo="", date=):
# TodayQue
# question_uuid:,question: memo:,saved_date:
@api.route('/memo_list/<string:user_uuid>')
class memo_list(Resource):
    def get(self, user_uuid):
        records = db.session.query(TodayQue).filter(TodayQue.user_uuid == user_uuid).all()
        if(not records):
            return []
        memo_list = []
        for record in records:
            print(1)
            question = db.session.query(CommonQue).get(record.today_ques).question
            print(question)
            memo_list.append({"question_uuid":record.today_ques,\
                "question":question,"memo":record.user_memo,\
                    "saved_date":turn_datetime_to_longint(record.date)})
        return jsonify(memo_list)
#def __init__(self, user_uuid, git_nickname, interesting_field, name, email, att_continue=0)

def make_list_to_string(input_list):
    ret_str = ""
    for element in input_list:
        ret_str += element + ','
    ret_str = ret_str[0:-1]
    return ret_str
@api.route('/interesting_field/<string:user_uuid>')
class interest_list(Resource):
    def get(self, user_uuid):
         raw_interest_list = db.session.query(User).filter(User.user_uuid == user_uuid).first()
         interest_list = raw_interest_list.interesting_field.split(',')
         ret = []
         for subject in default_interest_list:
            if subject in interest_list:
                ret.append({"selected":True, "field_name":subject})
            else:
                ret.append({"selected":False, "field_name":subject})
         return jsonify(ret)
    def put(self, user_uuid):
        interest_list = request.get_json()['interesting_field']
        #interest_list = ['c++', 'java', 'os'] # testcode
        print(interest_list)
        processed_list = make_list_to_string(interest_list)
        try:
            user = db.session.query(User).filter(User.user_uuid==user_uuid).first()
            user.interesting_field = processed_list
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, user_uuid):
        try:
            user = db.session.query(User).filter(User.user_uuid==user_uuid).first()
            user.interesting_field = ""
            db.session.commit()
        except:
            return 0
        return 1

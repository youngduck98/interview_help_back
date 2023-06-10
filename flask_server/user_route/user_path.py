from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.expression import func
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommendation, CommunityComment, JobObjectField, InterestOptionField, \
    UserInterest
from database.list import default_interest_list
from database.dictionary import ques_type_dict
from function.about_time import date_return, turn_datetime_to_longint
from function.about_string import *
from datetime import datetime, timedelta, date, time, timezone
import pytz, uuid, json, random
import os
from question.generate import GenerateQues
from github import Github

user_ab = Blueprint('user', __name__)
api = Api(user_ab) # api that make restapi more easier

@api.route('/git_lang/')
class git_lang(Resource):
    def get(self):
        # get a user by their GitHub username
        num_of_item = int(request.args.get('num'))
        user_uuid = request.args.get('uuid')
        github_token = os.environ.get('GITHUB_TOKEN')
        nickname = User.query.get(user_uuid).git_nickname
        print(nickname)
        try: 
            user = Github(github_token).get_user(nickname)
        except:
            return []

        language_dict = {}
        all_num = 1

        for repo in user.get_repos():
            # Get the programming languages used in this repository
            repo_languages = repo.get_languages()
            # Append the programming languages to the list of languages used by the user
            for language in repo_languages:
                if  language not in language_dict:
                    language_dict[language] = repo_languages[language]
                else:
                    language_dict[language] += repo_languages[language]
                all_num += repo_languages[language]
        lang_list = [{"lang":k,"percent":round(v/all_num * 100, 2)} for k, v in language_dict.items()]
        lang_list.sort(key=lambda x:x["percent"], reverse=True)
        
        if(num_of_item >= len(lang_list)):
            return lang_list
        
        lang_list = lang_list[:num_of_item - 1]
        
        etc_p = 100
        for element in lang_list:
            etc_p -= element['percent']
            
        lang_list.append({"lang":"기타", "percent":etc_p})

        # Print the list of programming languages used by the user
        return lang_list
        
@api.route('/git_nick/')
class git_nick(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        try:
            git_nick = User.query.get(user_uuid).git_nickname
        except:
            return 0
        return git_nick
    def put(self):
        user_uuid = request.args.get('user_uuid')
        git_nickname = request.args.get('git_nick')
        try:
            user = User.query.get(user_uuid)
            user.git_nickname = git_nickname
            db.session.commit()
        except:
            return False
        return True

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
        ret1 = int(turn_datetime_to_longint(fromdate))
        ret2 = int(turn_datetime_to_longint(todate))
        return jsonify({"from":ret1,"to": ret2})

#def __init__(self, att_uuid, user_uuid, att_date = datetime.now(pytz.timezone('Asia/Seoul'))):
@api.route('/today_attendance/<string:uuid2>')
class attendance(Resource):
    def get(self, uuid2):
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        fromdate, todate = date_return(today, 0)
        #check user_uuid is exist
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date <= todate).all()
        if(user_record):
            print("accepted")
            return 1
        print("rejected")
        return 0
    def post(self, uuid2):
        new_att_uuid = uuid.uuid1()
        today = datetime.now(pytz.timezone('Asia/Seoul'))
        fromdate, todate = date_return(today, -1)
        try:
            target_user = User.query.get(uuid2)
        except:
            print("no target")
            return 0
        user_record = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date <= todate).first()
        fromdate, todate = date_return(today, 0)
        user_record2 = Attendance.query.filter(Attendance.user_uuid == uuid2,\
                Attendance.att_date>=fromdate, Attendance.att_date <= todate).first()
        if(user_record and not user_record2):
            target_user.att_continue+=1
        elif(not user_record):
            target_user.att_continue=1
        db.session.commit()
        if(not user_record2):
            try:
                new_attd = Attendance(new_att_uuid, uuid2)
                db.session.add(new_attd)
                print(new_attd.att_date)
                db.session.commit()
            except:
                print("error in commit")
                return 0
            return 1
        print("attendance already done")
        return 0
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
        week_att = week_att[0:today.weekday()+1]
        return week_att            

@api.route('/change_today_question/')
class change_today_question(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        raw_interest_list = db.session.query(UserInterest).filter(UserInterest.user_uuid == user_uuid).all()
        interest_list = [x.interest_type for x in raw_interest_list]
        category = interest_list[random.randint(0, len(interest_list) - 1)]
        current_ques_uuid = request.args.get('current_ques_uuid')
        que_record = db.session.query(CommonQue).filter(CommonQue.ques_uuid != current_ques_uuid, CommonQue.ques_type == category).\
            order_by(func.random()).first()
        if(que_record):
            interestfield_record = InterestOptionField.query.all()
            ques_type_name_dict = {x.type:x.name for x in interestfield_record}
            que_type = ques_type_name_dict[que_record.ques_type]
            return jsonify({"ques_uuid":que_record.ques_uuid, "question": que_record.question, \
                "ques_type": que_type})
        return 0

@api.route('/suggest_common_ques/')
class add_common_ques(Resource):
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

@api.route('/first_today_question/')
class first_today_question(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        
        record = UserInterest.query.filter(UserInterest.user_uuid == user_uuid).all()
        if(not record):
            return None
        interest_type_list = [x.interest_type for x in record]
        category = interest_type_list[random.randint(0, len(interest_type_list) - 1)]
        
        que_record = db.session.query(CommonQue).filter(CommonQue.ques_type == category).\
            order_by(func.random()).first()
        if(not que_record):
            que_record = db.session.query(CommonQue).order_by(func.random()).first()
            
        interestfield_record = InterestOptionField.query.all()
        ques_type_name_dict = {x.type:x.name for x in interestfield_record}
        que_type = ques_type_name_dict[que_record.ques_type]
        return jsonify({"ques_uuid":que_record.ques_uuid, "question": que_record.question, \
                "ques_type": que_type})
#def __init__(self, tq_uuid, user_uuid, today_ques, user_memo="", date=)
@api.route('/common_ques_memo/')
class commmon_ques_memo(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.today_ques == common_ques_uuid,\
            TodayQue.user_uuid == user_uuid).first()
        if(record):
            question = db.session.query(CommonQue.ques_uuid, CommonQue.question).\
                filter(CommonQue.ques_uuid == record.today_ques).first()
            dt = int(turn_datetime_to_longint(record.date))
            return jsonify({"question_uuid":question.ques_uuid, "question":question.question,\
                "memo":record.user_memo, "saved_date":dt})
        return None
    def put(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.today_ques == common_ques_uuid,\
            TodayQue.user_uuid == user_uuid).first()
        
        if(record):
            try:
                record.user_memo = request.get_json()['memo']
                db.session.commit()
            except:
                return 0
            return 1
        
        try:
            record = TodayQue(uuid.uuid1(), user_uuid, common_ques_uuid, request.get_json()['memo'])
            db.session.add(record)
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self):
        user_uuid = request.args.get('user_uuid')
        common_ques_uuid = request.args.get('common_ques_uuid')
        record = db.session.query(TodayQue).filter(TodayQue.today_uuid == common_ques_uuid,\
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
                    "saved_date":int(turn_datetime_to_longint(record.date))})
        return jsonify(memo_list)
#def __init__(self, user_uuid, git_nickname, interesting_field, name, email, att_continue=0)

@api.route('/interesting_field/<string:user_uuid>')
class interest_list(Resource):
    def get(self, user_uuid):
        raw_interest_records = UserInterest.query.filter(UserInterest.user_uuid == user_uuid).all()
        interest_list = [x.interest_type for x in raw_interest_records]
        interest_all_list = [x.type for x in InterestOptionField.query.all()]
        ret = []
        for interest_type in interest_all_list:
            subject = InterestOptionField.query.get(interest_type).name
            if interest_type in interest_list:
                ret.append({"selected":True, "field_name":subject})
            else:
                ret.append({"selected":False, "field_name":subject})
        return jsonify(ret)
    def put(self, user_uuid):
        interest_list = request.get_json()['interesting_field']
        if "common" not in interest_list:
            interest_list.append("common")
        try:
            old_records = UserInterest.query.filter(UserInterest.user_uuid == user_uuid).all()
            for old_record in old_records:
                db.session.delete(old_record)
            interest_dict = {x.name:x.type for x in InterestOptionField.query.all()}
            for interest_type in interest_list:
                record = UserInterest(user_uuid, interest_dict[interest_type])
                db.session.add(record)
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, user_uuid):
        try:
            old_records = UserInterest.query.filter(UserInterest.user_uuid == user_uuid, \
                UserInterest.interest_type != "common").all()
            for old_record in old_records:
                db.session.delete(old_record)
            db.session.commit()
        except:
            return 0
        return 1

@api.route('/make_indivisual_ques/')
class make_indivisual_ques(Resource):
    def post(self):
        user_uuid = request.args.get('user_uuid')
        script_uuid = request.args.get('script_uuid')
        ques_num = int(request.args.get('ques_num'))
        ques_uuid_list = SynthesisSelfIntroduction.query.get(script_uuid).question.split(',')
        question = []
        answer = []
        
        db.session.delete()
        
        for ques_uuid in ques_uuid_list:
            question.append(SelfIntroductionQ.query.get(ques_uuid).question)
            answer.append(SelfIntroductionA.query.filter(SelfIntroductionA.script_ques_uuid == ques_uuid, \
                SelfIntroductionA.user_uuid == user_uuid).first().answer)
            
        ret = GenerateQues(contents_q=question, contents_a=answer, num_pairs= ques_num).genQues()
        for i in range(ques_num):
            db.session.add(IndividualQue(uuid.uuid1(), user_uuid, script_uuid, ret[i]))
        db.session.commit()
        return ret
        
@api.route('/job_object_list/')
class job_object_list(Resource):
    def get(self):
        ret = []
        for record in JobObjectField.query.filter().all():
            ret.append(record.object_name)
        return jsonify(ret)

@api.route('/interest_option_list')
class interest_option_list(Resource):
    def get(self):
        ret = []
        for record in InterestOptionField.query.filter().all():
            ret.append(record.object_name)
        return jsonify(ret)
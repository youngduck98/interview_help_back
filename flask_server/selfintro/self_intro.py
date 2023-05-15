from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.expression import func
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommendation, CommunityComment, JobObjectField, InterestOptionField
from database.list import default_interest_list
from database.dictionary import ques_type_dict
from function.about_time import date_return, turn_datetime_to_longint
from datetime import datetime, timedelta, date, time, timezone
import pytz, uuid, json, random

selfintro_ab = Blueprint('selfintro', __name__)
api = Api(selfintro_ab) # api that make restapi more easier

@api.route('/main')
class check_selfintro_ab(Resource):
    def get(self):
        return "this is selfintro main page\n"
#make scriptiem(question list in script)

def make_script_item(que_uuid_list, script_uuid):
    que_list = []
    for que_uuid in que_uuid_list:
        que_record = db.session.query(SelfIntroductionQ).filter(\
            SelfIntroductionQ.script_ques_uuid == que_uuid).first()
        answer_record = db.session.query(SelfIntroductionA).filter(\
            SelfIntroductionA.script_ques_uuid == que_uuid, SelfIntroductionA.script_uuid == script_uuid).first()
        answer=""
        if(answer_record):
            answer = answer_record.answer
        tips = que_record.tip.split(',')
        que_list.append({"index":que_record.index, "script_item_uuid":que_record.script_ques_uuid,\
            "script_item_question":que_record.question, \
                "script_item_answer": answer, \
                    "script_item_answer_max_length": que_record.max_answer_len, \
                    "tips":tips})
    return que_list

def return_script(script_uuid, user_uuid):
    record = db.session.query(SynthesisSelfIntroduction).filter(\
        SynthesisSelfIntroduction.script_uuid==script_uuid, \
            SynthesisSelfIntroduction.script_host == user_uuid).first()
    print(record)
    print(script_uuid, user_uuid)
    que_uuid_list = record.question.split(',')
    que_list = make_script_item(que_uuid_list, script_uuid)
    interviewed = False
    if(record.interview == 1):
        interviewed = True
    ret = {"script_uuid":record.script_uuid, \
        "script_date":int(turn_datetime_to_longint(record.script_date)), \
        "script_title":record.script_title, "script_items":que_list, \
            "interviewed": interviewed}
    return ret

def make_script(user_uuid, script_title, que_ans_list):
    ques_string=""
    for que_ans in que_ans_list:
        ques_uuid = que_ans['question_uuid']
        ques_record = db.session.query(SelfIntroductionQ).get(ques_uuid)
        if(not ques_record):
            return False
        ques_string += "," + ques_record.script_ques_uuid
    ques_string = ques_string[1:]
    today = datetime.now(pytz.timezone('Asia/Seoul'))
    ret = uuid.uuid1()
    script_record = SynthesisSelfIntroduction(ret, user_uuid, today, \
        script_title, ques_string)
    db.session.add(script_record)
    db.session.commit()
    
    for que_ans in que_ans_list:
        ques_uuid = que_ans['question_uuid']
        answer = que_ans['answer']
        answer_record = SelfIntroductionA.query.filter(SelfIntroductionA.user_uuid == user_uuid, \
            SelfIntroductionA.script_uuid == ret, SelfIntroductionA.script_ques_uuid == ques_uuid).first()
        if (answer_record):
            answer_record.answer = answer
        else:
            answer_record = SelfIntroductionA(uuid.uuid1(), user_uuid, ques_uuid, answer, ret)
            try:
                db.session.add(answer_record)
            except:
                return False
        db.session.commit()
    
    return str(ret)
            
@api.route('/script/')
class self_intro_script(Resource):
    def get(self):
        script_uuid = request.args.get('script_uuid')
        user_uuid = request.args.get('user_uuid')
        return jsonify(return_script(script_uuid, user_uuid))
    def post(self):
        user_uuid = request.args.get('user_uuid')
        script_title = request.get_json()['script_title']
        que_ans_list = request.get_json()['items']
        return make_script(user_uuid, \
            script_title, que_ans_list)
    def put(self):
        user_uuid = request.args.get('user_uuid')
        script_uuid = request.args.get('script_uuid')
        ques_uuid = request.get_json()['question_uuid']
        answer = request.get_json()['answer']
        # script_ans_uuid, user_uuid, script_ques_uuid, answer
        record = db.session.query(SelfIntroductionA).filter(\
            SelfIntroductionA.user_uuid == user_uuid,\
                SelfIntroductionA.script_ques_uuid == ques_uuid, \
                    SelfIntroductionA.script_uuid == script_uuid).first()
        record.answer = answer
        db.session.commit()
        return 1

#script_uuid, script_host, script_date, script_title, question
@api.route('/script_list/<string:user_uuid>')
class script_list(Resource):
    def get(self, user_uuid):
        script_records = db.session.query(SynthesisSelfIntroduction).\
            filter(SynthesisSelfIntroduction.script_host == user_uuid).all()
        ret = []
        for sr in script_records:
            question_list = sr.question.split(',')
            print(question_list)
            ret.append(return_script(sr.script_uuid, user_uuid))
            """
            ret.append({"script_uuid":sr.script_uuid, \
                "script_date": int(sr.script_date.timestamp()*1000), \
                    "script_title": sr.script_title, \
                        "script_items": make_script_item(question_list, sr.script_uuid), \
                            })
            """
        return ret

@api.route('/all_question/')
class script_question(Resource):
    def get(self):
        script_uuid = request.args.get('script_uuid')
        if(not script_uuid):
            script_uuid = "00001"
        ques_uuid_list = db.session.query(SynthesisSelfIntroduction).get(script_uuid).question.split(',')
        ret = []
        for ques_uuid in ques_uuid_list:
            que_record = db.session.query(SelfIntroductionQ).get(ques_uuid)
            if(not que_record):
                return 0
            question = que_record.question
            index = que_record.index
            tips = que_record.tip.split(',')
            ret.append({"index":index, "question":question, "tips":tips})
        return ret
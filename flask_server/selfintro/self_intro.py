from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.expression import func
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommendation, CommunityComment, JobObjectField, InterestOptionField
from database.list import default_interest_list
from database.dictionary import ques_type_dict
from function.about_time import date_return, turn_datetime_to_longint, today_return
from function.about_string import make_list_to_string
from datetime import datetime, timedelta, date, timezone
import pytz, uuid, json, random
from dataclasses import dataclass
from question.generate import GenerateQues
from dataclasses_json import dataclass_json
import time
import asyncio

selfintro_ab = Blueprint('selfintro', __name__)
api = Api(selfintro_ab) # api that make restapi more easier

@api.route('/main')
class check_selfintro_ab(Resource):
    def get(self):
        return "this is selfintro main page\n"
#make scriptiem(question list in script)

@dataclass_json
@dataclass
class ScriptItem:
    index:int
    script_item_uuid:str
    script_item_question:str
    script_item_answer:str
    script_item_answer_max_length:int
    tips:'list[str]'
    

@dataclass_json
@dataclass
class self_intoduction_script:
    script_uuid: str
    host_uuid: str
    date: int
    script_title: str
    script_items: 'list[ScriptItem]'
    interviewed: bool
    role: str

def make_indivisual_ques(user_uuid:str, script_uuid:str, ques_num:int):
    ques_uuid_list = SynthesisSelfIntroduction.query.get(script_uuid).question.split(',')
    question = []
    answer = []
    try:
        for ques_uuid in ques_uuid_list:
            question.append(SelfIntroductionQ.query.get(ques_uuid).question)
            answer.append(SelfIntroductionA.query.filter(SelfIntroductionA.script_ques_uuid == ques_uuid, \
                SelfIntroductionA.user_uuid == user_uuid).first().answer)
        
        print("question")
        print(question)
        print("answer")
        print(answer)
        
        ret = GenerateQues(contents_q=question, contents_a=answer, num_pairs= ques_num).genQues()
        for i in range(ques_num):
            db.session.add(IndividualQue(uuid.uuid1(), user_uuid, script_uuid, ret[i]))
        db.session.commit()
    except:
        return False
    return True

def make_individual(script_uuid:str, host_uuid:str):
    record = SynthesisSelfIntroduction.query.get(script_uuid)
    state = False
    print("start to make question")
    record.interview_ready = 0
    while not state :
        state = make_indivisual_ques(host_uuid, script_uuid, 2)
    record.interview_ready = 1
    db.session.commit()
    print("end to make question")

def make_script_item(que_uuid_list, script_uuid=False):
    que_list = []
    for que_uuid in que_uuid_list:
        que_record = SelfIntroductionQ.query.get(que_uuid)
        
        answer=""
        if(script_uuid):
            answer_record = db.session.query(SelfIntroductionA).filter(\
                SelfIntroductionA.script_ques_uuid == que_uuid, SelfIntroductionA.script_uuid == script_uuid).first()
            if(answer_record):
                answer = answer_record.answer
        if(que_record.tip):
            tips = que_record.tip.split(',')
        else:
            tips = []
        que_list.append(ScriptItem(que_record.index, que_record.script_ques_uuid, \
            que_record.question, answer, que_record.max_answer_len, tips))
        
    return que_list
    #return jsonify(que_list)

def return_script(script_uuid, user_uuid):
    record = db.session.query(SynthesisSelfIntroduction).filter(\
        SynthesisSelfIntroduction.script_uuid==script_uuid, \
            SynthesisSelfIntroduction.script_host == user_uuid).first()
    if(not record):
        return False
    role = JobObjectField.query.get(record.objective).object_name
    print(record)
    print(script_uuid, user_uuid)
    que_uuid_list = record.question.split(',')
    
    #que_list = make_script_item(que_uuid_list, script_uuid)
    script_item_list = make_script_item(que_uuid_list, script_uuid)
    interviewed = False
    
    if(record.interview == 1):
        #test
        interviewed = True
        check_record = MockInterview.query.filter(MockInterview.referenced_script == script_uuid\
            , MockInterview.score > -1).all()
        if(check_record):
            interviewed = True
    
    ret = self_intoduction_script(record.script_uuid, user_uuid, turn_datetime_to_longint(record.script_date), \
        record.script_title, script_item_list, interviewed, role)
    
    return ret

def make_script(new_script:self_intoduction_script):
    ques_string=""
    for script_item in new_script.script_items:
        #script_item = ScriptItem(script_item)
        ques_record = db.session.query(SelfIntroductionQ).get(script_item.script_item_uuid)
        if(not ques_record):
            return 0
        ques_string += "," + ques_record.script_ques_uuid
    ques_string = ques_string[1:] # need to improve when DB Normalization
    today = datetime.now(pytz.timezone('Asia/Seoul'))
    
    job_field_records = JobObjectField.query.all()
    object_name_type_dict = {x.object_name:x.object_type for x in job_field_records}
    new_role = object_name_type_dict[new_script.role]
    
    script_record = SynthesisSelfIntroduction(new_script.script_uuid, new_script.host_uuid, today, \
        new_script.script_title, ques_string, 0, new_role)
    db.session.add(script_record)
    db.session.commit()
    
    for script_item in new_script.script_items:
        #script_item = ScriptItem(script_item)
        ques_uuid = script_item.script_item_uuid
        answer = script_item.script_item_answer
        answer_record = SelfIntroductionA.query.filter(SelfIntroductionA.user_uuid == new_script.host_uuid, \
            SelfIntroductionA.script_uuid == new_script.script_uuid, \
                SelfIntroductionA.script_ques_uuid == ques_uuid).first()
        if (answer_record):
            answer_record.answer = answer
        else:
            answer_record = SelfIntroductionA(uuid.uuid1(), new_script.host_uuid, \
                ques_uuid, answer, new_script.script_uuid)
            try:
                db.session.add(answer_record)
            except:
                return 0
        db.session.commit()
    print(4)
    #make_individual(new_script)
    return 1

def update_script(new_script:self_intoduction_script):
    script_record = SynthesisSelfIntroduction.query.get(new_script.script_uuid)
    if(not script_record):
        return 0
    IndividualQue_records = IndividualQue.query.filter(IndividualQue.script_uuid == new_script.script_uuid).all()
    if(IndividualQue_records):
        for indiv_record in IndividualQue_records:
            db.session.delete(indiv_record)
    db.session.commit()
    
    script_record.script_host = new_script.host_uuid
    script_record.script_date = datetime.fromtimestamp(int(new_script.date/1000))
    script_record.script_title = new_script.script_title
    script_record.interview = 0
    
    job_field_records = JobObjectField.query.all()
    object_name_type_dict = {x.object_name:x.object_type for x in job_field_records}
    script_record.objective = object_name_type_dict[new_script.role]
    
    old_question_uuid = script_record.question.split(",")
    
    for script_item, old_que_uuid in \
        zip(new_script.script_items, old_question_uuid):
        #script_item = ScriptItem(script_item)
        new_record_Q = SelfIntroductionQ.query.get(script_item.script_item_uuid)
        new_record_A = SelfIntroductionA.query.filter(
            SelfIntroductionA.script_uuid == new_script.script_uuid, \
                SelfIntroductionA.script_ques_uuid == old_que_uuid).first()
        new_record_Q.question = script_item.script_item_question
        new_record_Q.index = script_item.index
        new_record_Q.tip = make_list_to_string(script_item.tips)
        
        new_record_A.script_ques_uuid = script_item.script_item_uuid
        new_record_A.answer = script_item.script_item_answer
    
    db.session.commit()
    print(3)
    #make_individual(new_script)
    return 1

@api.route('/make_indiv_question/')
class make_indiv_question(Resource):
    def post(self):
        try:
            script = self_intoduction_script.from_json(json.dumps(request.get_json()))
            make_individual(script)
        except:
            print("error while make_indiv_question")
            return False
        return True
        
        
@api.route('/script/')
class self_intro_script(Resource):
    def get(self):
        script_uuid = request.args.get('script_uuid')
        user_uuid = request.args.get('user_uuid')
        ret = return_script(script_uuid, user_uuid).to_json()
        ret = json.loads(ret)
        ret = jsonify(ret)
        return ret
    def post(self):
        script = self_intoduction_script.from_json(json.dumps(request.get_json()))
        record = SynthesisSelfIntroduction.query.get(script.script_uuid)
        if(record):
            while(record.interview_ready == 0):
                time.sleep(0.5)
            print("wait end")
            return update_script(script)
        return make_script(script)
    def delete(self):
        script_uuid = request.args.get('script_uuid')
        user_uuid = request.args.get('user_uuid')
        record = SynthesisSelfIntroduction.query.get(script_uuid)
        
        if(record.script_host != user_uuid):
            return False
        
        with db.engine.connect() as connection:
            connection.execute("DELETE FROM SynthesisSelfIntroduction WHERE script_uuid = %s", \
                script_uuid)
        return True
        
#script_uuid, script_host, script_date, script_title, question
@api.route('/script_list/<string:user_uuid>')
class script_list(Resource):
    def get(self, user_uuid):
        script_records = db.session.query(SynthesisSelfIntroduction).\
            filter(SynthesisSelfIntroduction.script_host == user_uuid).all()
        ret = []
        for sr in script_records:
            script_json = return_script(sr.script_uuid, user_uuid).to_json()
            script_json = json.loads(script_json)
            ret.append(script_json)
        return jsonify(ret)

@api.route('/all_question/')
class script_question(Resource):
    def get(self):
        records = SelfIntroductionQ.query.all()
        que_uuid_list = [record.script_ques_uuid for record in records]
        ret = []
        for item in make_script_item(que_uuid_list):
            item = item.to_json()
            item = json.loads(item)
            ret.append(item)
        return jsonify(ret)
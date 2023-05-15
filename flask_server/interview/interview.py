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

interview_ab = Blueprint('interview', __name__)
api = Api(interview_ab) # api that make restapi more easier

@api.route('/main/')
class interview_main(Resource):
    def get(self):
        return "interview_main"

def select_common_from_types(raw_interest_type_list):
    slected_type = []
    common_que_record = []
    
        #select common_que
    if(len(raw_interest_type_list) != 0):
        for i in range(3):
            slected_type.append(raw_interest_type_list[random.randrange(0, len(raw_interest_type_list))])
        
        records = db.session.query(CommonQue).filter(CommonQue.ques_type == i).\
                order_by(func.random())
        for i in slected_type:
            offset = 0
            new_q = records.offset(offset).first()
            while(new_q in common_que_record):
                new_q = records.offset(offset).first()
                offset+=1
            common_que_record.append(new_q)
    else:
        for i in range(3):
            offset = 0
            new_q = records.offset(offset).first()
            while(new_q in common_que_record):
                new_q = records.offset(offset).first()
                offset+=1
            common_que_record.append(new_q)
    return common_que_record

@api.route('/interview/')
class interview(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        script_uuid = request.args.get('script_uuid')
        reuse = request.args.get('reuse_questionnaire')
        
        raw_interest_type_list = db.session.query(User).filter(User.user_uuid == user_uuid).\
            first().interesting_field.split(',')
        
        slected_type = []
        common_que_records = select_common_from_types(raw_interest_type_list)
        indiv_que_records = IndividualQue.query().filter(IndividualQue.script_uuid == script_uuid).\
            order_by(func.random()).limit(3).all()
        
        return 1
            
        
                
        
        
        
        
        
        
        

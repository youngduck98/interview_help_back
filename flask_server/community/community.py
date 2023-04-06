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

community_ab = Blueprint('community', __name__)
api = Api(community_ab) # api that make restapi more easier

@api.route('/main')
class check_selfintro_ab(Resource):
    def get(self):
        return "this is community main page\n"

#/sef_intro/view_comment/?page=<int>&per_page=<int>&question_uuid=<string>
@api.route('/view_comment/')
class view_comment(Resource):
    def get(self):
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        question_uuid = request.args.get('ques_uuid')
        page_offset = (page-1)*per_page
        
        comment_records = db.session.query(CommunityComment).\
            filter(CommunityComment.common_ques == question_uuid).\
                order_by(CommunityComment.recommendation.desc()).\
                    offset(page_offset).limit(int(per_page)).all()
        ret = []
        if(not comment_records):
            return ret
        
        for cr in comment_records:
            ret.append({"cc_uuid":cr.cc_uuid,\
                "user_uuid":cr.user_uuid, "common_ques":cr.common_ques, \
                        "comment":cr.comment, "date":cr.date.timestamp()*1000, "recommendation":cr.recommendation})
        
        #cc_uuid, user_uuid, common_ques, comment, date, recommendation
        return jsonify(ret)

#/community/recommendation/?cc_uuid=<string>& user_uuid=<string>
@api.route('/community/recommendation')
class recommendation(Resource):
    def get(self):
        cc_uuid = request.args.get('cc_uuid')
        record = db.session.query(CommunityComment).\
            filter(CommunityComment.cc_uuid == cc_uuid).first()
        
        if(not record):
            return None
        #cc_uuid, user_uuid, common_ques, comment, date, recommendation
        return record.recommendation
        
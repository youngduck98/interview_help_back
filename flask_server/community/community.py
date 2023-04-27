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
@api.route('/recommendation/')
class recommendation(Resource):
    def get(self):
        cc_uuid = request.args.get('cc_uuid')
        record = db.session.query(CommunityComment).\
            filter(CommunityComment.cc_uuid == cc_uuid).first()
        
        if(not record):
            return None
        #cc_uuid, user_uuid, common_ques, comment, date, recommendation
        return record.recommendation
    def post(self):
        cc_uuid = request.args.get('cc_uuid')
        user_uuid = request.args.get('user_uuid')
        cc_record = db.session.query(CommunityComment).\
            filter(CommunityComment.cc_uuid == cc_uuid).first()
        check_cr_record = db.session.query(CommentRecommendation).\
            filter(CommentRecommendation.cc_uuid == cc_uuid,\
                CommentRecommendation.user_uuid == user_uuid).first()
        check_user_record = db.session.query(User).get(user_uuid)
        
        if(not check_user_record):
            return -2 # not user
        elif(check_cr_record):
            return -1 # already recommend
        else:
            #cc_uuid, user_uuid, common_ques, comment, date, recommendation
            cc_record.recommendation += 1
            new_cr_record = CommentRecommendation(uuid.uuid1(), user_uuid, cc_uuid)
            db.session.add(new_cr_record)
            db.session.commit()
            return cc_record.recommendation
    def put(self):
        cc_uuid = request.args.get('cc_uuid')
        num = request.args.get('recommend')
        try:
            cc_record = db.session.query(CommunityComment).\
                filter(CommunityComment.cc_uuid == cc_uuid).first()
            cc_record.recommendation = num
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self):
        cc_uuid = request.args.get('cc_uuid')
        user_uuid = request.args.get('user_uuid')
        cc_record = db.session.query(CommunityComment).\
            filter(CommunityComment.cc_uuid == cc_uuid).first()
        check_cr_record = db.session.query(CommentRecommendation).\
            filter(CommentRecommendation.cc_uuid == cc_uuid,\
                CommentRecommendation.user_uuid == user_uuid).first()
        check_user_record = db.session.query(User).get(user_uuid)
        if(not check_cr_record):
            return -1
        db.session.delete(check_cr_record)
        cc_record.recommendation -= 1
        if(cc_record.recommendation < 0):
            cc_record.recommendation = 0
        db.session.commit()
        return cc_record.recommendation

@api.route('/comment/')
class comment(Resource):
    def post(self):
        try:
            cc_uuid = request.args.get('cc_uuid')
            ques_uuid = request.get_json()['ques_uuid']
            user_uuid = request.get_json()['user_uuid']
            comment = request.get_json()['comment']
            cc_record = db.session.query(CommunityComment).get(cc_uuid)
            if(cc_record):
                return 0
            new_cc_record = CommunityComment(cc_uuid, user_uuid, ques_uuid, comment)
            db.session.add(new_cc_record)
            db.session.commit()
        except:
            return 0
        return 1
    def put(self):
        try:
            cc_uuid = request.args.get('cc_uuid')
            comment = request.get_json()['comment']
            cc_record = db.session.query(CommunityComment).get(cc_uuid)
            cc_record.comment = comment
            db.session.commit()
        except:
            return 0
    def delete(self):
        cc_uuid = request.args.get('cc_uuid')
        cc_record = db.session.query(CommunityComment).get(cc_uuid)
        cr_records = db.session.query(CommentRecommendation).filter(CommentRecommendation.cc_uuid == cc_uuid).all()
        for cr in cr_records:
            db.session.delete(cr)
        db.session.commit()
        print(1)
        if(not cc_record):
            return 0
        db.session.delete(cc_record)
        db.session.commit()
        return 1
    
        
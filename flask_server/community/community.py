from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.expression import func
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommendation, CommunityComment
from database.list import default_interest_list
from database.dictionary import ques_type_dict
from function.about_time import date_return, turn_datetime_to_longint, today_return
from datetime import datetime, timedelta, date, time, timezone
import pytz, uuid, json, random

community_ab = Blueprint('community', __name__)
api = Api(community_ab) # api that make restapi more easier

@api.route('/main')
class check_selfintro_ab(Resource):
    def get(self):
        return "this is community main page\n"

@api.route('/view_comment/')
class view_comment(Resource):
    def get(self):
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        question_uuid = request.args.get('ques_uuid')
        viewer_uuid = request.args.get('user_uuid')
        page_offset = (page-1)*per_page
        
        comment_records = db.session.query(CommunityComment).\
            filter(CommunityComment.common_ques == question_uuid).\
                order_by(CommunityComment.recommendation.desc()).\
                    offset(page_offset).limit(int(per_page)).all()
        
        ret = []
        if(not comment_records):
            return ret
        
        for cr in comment_records:
            ur = User.query.get(cr.user_uuid)
            cr_uuid = CommentRecommendation.query.filter(CommentRecommendation.cc_uuid == cr.cc_uuid, \
                CommentRecommendation.user_uuid == viewer_uuid).first()
            
            if(cr_uuid):
                vw_liked = True
            else:
                vw_liked = False
                
            ret.append({"cc_uuid":cr.cc_uuid,\
                "user_uuid":cr.user_uuid, "common_ques":cr.common_ques, \
                        "comment":cr.comment, "date":int(turn_datetime_to_longint(cr.date)), \
                            "recommendation":cr.recommendation, "name": ur.name, \
                                "email":ur.email, "viewer_liked": vw_liked})
        
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
    def put(self):
        cc_uuid = request.args.get('cc_uuid')
        user_uuid = request.args.get('user_uuid')
        cc_record = db.session.query(CommunityComment).\
            filter(CommunityComment.cc_uuid == cc_uuid).first()
        check_cr_record = db.session.query(CommentRecommendation).\
            filter(CommentRecommendation.cc_uuid == cc_uuid,\
                CommentRecommendation.user_uuid == user_uuid).first()
        check_user_record = db.session.query(User).get(user_uuid)
        
        if(not cc_record):
            return -2
        
        if(not check_user_record):
            return -1 # not user
        elif(check_cr_record):
            cc_record.recommendation -= 1
            db.session.delete(check_cr_record)
        else:
            #cc_uuid, user_uuid, common_ques, comment, date, recommendation
            cc_record.recommendation += 1
            new_cr_record = CommentRecommendation(uuid.uuid1(), user_uuid, cc_uuid)
            db.session.add(new_cr_record)
        db.session.commit()
        return cc_record.recommendation
    
@api.route('/comment/')
class comment(Resource):
    def post(self):
        try:
            cc_uuid = uuid.uuid1()
            ques_uuid = request.get_json()['ques_uuid']
            user_uuid = request.get_json()['user_uuid']
            comment = request.get_json()['comment']
            cc_record = db.session.query(CommunityComment).get(cc_uuid)
            if(cc_record):
                cc_record.comment = comment
            else:
                new_cc_record = CommunityComment(cc_uuid, user_uuid, ques_uuid, comment)
                db.session.add(new_cc_record)
            db.session.commit()
        except:
            return None
        user_record = User.query.get(user_uuid)
        return jsonify({"user_uuid": user_uuid, "cc_uuid": cc_uuid, "common_ques": ques_uuid,\
                "comment": comment, "date": int(today_return()), \
                    "recommendation": 0, "name": user_record.name, "email": user_record.email, \
                        "viewer_liked": False})
    def put(self):
        try:
            cc_uuid = request.args.get('cc_uuid')
            comment = request.get_json()['comment']
            cc_record = db.session.query(CommunityComment).get(cc_uuid)
            cc_record.comment = comment
            cc_record.date = datetime.now(pytz.timezone('Asia/Seoul'))
            db.session.commit()
        except:
            return None
        
        user_record = User.query.get(cc_record.user_uuid)
        return jsonify({"user_uuid": cc_record.user_uuid, "cc_uuid": cc_uuid, "common_ques": cc_record.common_ques,\
                "comment": comment, "date": int(today_return()), \
                    "recommendation": 0, "name": user_record.name, "email": user_record.email, \
                        "viewer_liked": False})
    def delete(self):
        cc_uuid = request.args.get('cc_uuid')
        user_uuid = request.args.get('user_uuid')
        cc_record = db.session.query(CommunityComment).get(cc_uuid)
        if(not cc_record or cc_record.user_uuid != user_uuid):
            return 0
        cr_records = db.session.query(CommentRecommendation).filter(CommentRecommendation.cc_uuid == cc_uuid).all()
        for cr in cr_records:
            db.session.delete(cr)
        db.session.commit()
        db.session.delete(cc_record)
        db.session.commit()
        return 1

@api.route('/view_my_comment/')
class my_comment(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        records = CommunityComment.query.filter(CommunityComment.user_uuid == user_uuid).all()
        user = User.query.get(user_uuid)
        
        ret = []
        
        if(not records):
            return None
        
        for record in records:
            cr = CommentRecommendation.query.filter(CommentRecommendation.cc_uuid == record.cc_uuid, \
                CommentRecommendation.user_uuid == user_uuid).first()
            if(cr): vw_liked = True
            else: vw_liked = False
            
            ret.append({"user_uuid": user_uuid, "cc_uuid": record.cc_uuid, "common_ques": record.common_ques,\
                "comment": record.comment, "date": int(turn_datetime_to_longint(record.date)), \
                    "recommendation": record.recommendation, "name": user.name, "email": user.email, \
                        "viewer_liked": vw_liked})
        
        return jsonify(ret[0])

@api.route('/view_my_ques_comment/')
class my_comment(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        ques_uuid = request.args.get('ques_uuid')
        record = CommunityComment.query.filter(CommunityComment.user_uuid == user_uuid, \
            CommunityComment.common_ques == ques_uuid).first()
        if not record:
            return None
        user = User.query.get(user_uuid)
        if not user:
            return None
        cr = CommentRecommendation.query.filter(CommentRecommendation.cc_uuid == ques_uuid, \
                CommentRecommendation.user_uuid == user_uuid).first()
            
        if(cr):
            vw_liked = True
        else:
            vw_liked = False
        
        return jsonify({"user_uuid": user_uuid, "cc_uuid": record.cc_uuid, "common_ques": record.common_ques,\
                "comment": record.comment, "date": int(turn_datetime_to_longint(record.date)), \
                    "recommendation": record.recommendation, "name": user.name, "email": user.email, \
                        "viewer_liked": vw_liked})
import sys, os, json
from flask import Flask, request, jsonify

from datetime import datetime
import pytz
import uuid

import config
from database.db_connect import db
from database import module
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommandation, CommunityComment
from database.dictionary import ques_type_dict

from sqlalchemy.sql.expression import func
    
from flask_restx import Resource, Api
from user_route import user_path
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from database import admin_view
import MySQLdb
#from database.module import User, Attendance, CommonQue, IndividualQue, MockInterview, SynthesisSelfIntroduction, SelfIntroductionA, SelfIntroductionQ, TodayQue, CommentRecommandation, CommunityComment

app = Flask(__name__) # app assignment
app.config.from_object(config) # app setting config through config object(related to DB)
db.init_app(app)
app.register_blueprint(user_path.user_ab, url_prefix='/user')

api = Api(app) # api that make restapi more easier

"""
# blueprint name에 기본적으로 user가 있다길래 그거 없애기 위한 것
# 이후 만약 문제 생기면 밑에 admin.add_view(ModelView(User, db.session))와 함께 지우면 됨
# ----------------------------------
user_blueprint = None
for bp in app.blueprints.values():
    if bp.name == 'user':
        user_blueprint = bp
        break

if user_blueprint:
    app.blueprints.pop(user_blueprint.name)
# ----------------------------------
    
# set flask_admin
admin = Admin(app, name='InterviewM@ster', template_mode='bootstrap3')
admin.add_view(admin_view.UserAdminView(module.User, db.session))
admin.add_view(admin_view.SynthesisSelfIntroductionAdminView(module.SynthesisSelfIntroduction, db.session))
#admin.add_view(ModelView(ItemSelfIntroduction, db.session))
admin.add_view(admin_view.CommonQueAdminView(module.CommonQue, db.session))
admin.add_view(admin_view.IndividualQueAdminView(module.IndividualQue, db.session))
admin.add_view(admin_view.AttendanceAdminView(module.Attendance, db.session))
# admin.add_view(ModelView(TodayQue, db.session))
admin.add_view(admin_view.MockInterviewAdminView(module.MockInterview, db.session))
#admin.add_view(ModelView(InterviewLog, db.session))
#admin.add_view(ModelView(Achievement, db.session))
#admin.add_view(ModelView(InterviewQuestion, db.session))
admin.add_view(admin_view.SelfIntroductionAAdminView(module.SelfIntroductionA, db.session))
admin.add_view(admin_view.SelfIntroductionQAdminView(module.SelfIntroductionQ, db.session))
admin.add_view(admin_view.TodayQueAdminView(module.TodayQue, db.session))
admin.add_view(admin_view.CommentRecommandationAdminView(module.CommentRecommandation, db.session))
admin.add_view(admin_view.CommunityCommentAdminView(module.CommunityComment, db.session))
"""

@api.route('/test/<string:uuid>')
class test(Resource):
    def get(self, uuid):
        try:
            nick = module.user_info_table.query.filter_by(user_uuid=uuid).first().git_nickname
        except:
            return 0
        return nick
    def post(self, uuid):
        try:
            data = request.get_json()['git_nickname']
            user_info = module.UserInfo(uuid, data)
            print(2)
            db.session.add(user_info)
            db.session.commit()
        except:
            return 0
        return 1
    def put(self, uuid):
        try:
            user_info = module.UserInfo.query.get(uuid)
            user_info.git_nickname = request.get_json()['git_nickname']
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, uuid):
        try:
            user_info = module.UserInfo.query.get(uuid)
            db.session.delete(user_info)
            db.session.commit()
        except:
            return 0
        return 1

@app.route('/main')
def main_page_mesg():
    return "this is capstone main page\n"

@api.route('/membership/<string:user_uuid>')
#def __init__(self, user_uuid, git_nickname, interesting_field, name, email, att_continue=0):
class user(Resource):
    def get(self, user_uuid):
        try:
            person = User.query.filter_by(User.user_uuid == user_uuid).first()
        except:
            return 0
        if person is None:
            return 0
        return 1
    def post(self, user_uuid):
        print(1)
        new_git_nickname = ""
        new_interesting_field = ""
        name = request.get_json()['name']
        email = request.get_json()['email']
        try:
            new_user = User(user_uuid, new_git_nickname, new_interesting_field, name, email, 0)
            db.session.add(new_user)
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, user_uuid):
        try:
            user = User.query.filter_by(User.user_uuid==user_uuid).first()
            db.session.delete(user)
            db.session.commit()
        except:
            return 0
        return 1

#def __init__(self, ques_uuid, question, ques_type=0, recommandation=0):
@api.route('/common_question/')
class common_question(Resource):
    def get(self):
        common_ques_uuid = request.args.get('common_ques_uuid')
        que_record = db.session.query(CommonQue).filter(CommonQue.ques_uuid == common_ques_uuid)
        if(que_record):
            return 1
        return 0
    def post(self):
        category = request.args.get('category')
        category = ques_type_dict[category]
        common_ques_uuid = request.args.get('common_ques_uuid')
        question = request.get_json()['question']
        new_record = CommonQue(common_ques_uuid, question, category)
        db.session.add(new_record)
        db.session.commit()
    def put(self):
        category = request.args.get('category')
        category = ques_type_dict[category]
        common_ques_uuid = request.args.get('common_ques_uuid')
        question = request.get_json()['question']
        try:
            record = db.session.query(CommonQue).get(common_ques_uuid)
            if(not record):
                return 0
            record.question = question
            db.session.commit()
        except:
            return 0
        return 1
    
@api.route('/gpttest/<string:script_uuid>')
class gpttest(Resource):
    def get(self, script_uuid):
        try:
            script_uuid = module.ItemSelfIntroduction.query.filter_by(script_item_uuid = script_uuid).first()
        except:
            return 0
        
        return script_uuid

if __name__ == "__main__":
    app.run(host = "0.0.0.0")

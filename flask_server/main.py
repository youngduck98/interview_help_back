import sys, os
from flask import Flask, request, jsonify

from datetime import datetime
import pytz

import config
from database.db_connect import db
from database import module
from flask_restx import Resource, Api
from user_route import user_path

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from database.module import User, Achievement, Attendance, CommonQue, IndividualQue, InterviewLog, InterviewQuestion, ItemSelfIntroduction, MockInterview, SynthesisSelfIntroduction

app = Flask(__name__) # app assignment
app.config.from_object(config) # app setting config through config object(related to DB)
db.init_app(app)
app.register_blueprint(user_path.user_ab, url_prefix='/user')

api = Api(app) # api that make restapi more easier

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
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(SynthesisSelfIntroduction, db.session))
admin.add_view(ModelView(ItemSelfIntroduction, db.session))
admin.add_view(ModelView(CommonQue, db.session))
admin.add_view(ModelView(IndividualQue, db.session))
admin.add_view(ModelView(Attendance, db.session))
# admin.add_view(ModelView(TodayQue, db.session))
admin.add_view(ModelView(MockInterview, db.session))
admin.add_view(ModelView(InterviewLog, db.session))
admin.add_view(ModelView(Achievement, db.session))
admin.add_view(ModelView(InterviewQuestion, db.session))

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
            user_info = module.user_info_table(uuid, data)
            db.session.add(user_info)
            db.session.commit()
        except:
            return 0
        return 1
    def put(self, uuid):
        try:
            user_info = module.user_info_table.get(uuid)
            user_info.git_nickname = request.get_json()['git_nickname']
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, uuid):
        try:
            user_info = module.user_info_table.get(uuid)
            db.session.delete(user_info)
            db.session.commit()
        except:
            return 0
        return 1

@app.route('/main')
def main_page_mesg():
    return "this is capstone main page\n"

@api.route('/membership/<string:uuid>')
class user(Resource):
    def get(self, uuid):
        try:
            person = module.User.query.filter_by(user_uuid = uuid).first()
        except:
            return 0
        if person is None:
            return 0
        return 1
    def post(self, uuid):
        new_git_nickname = ""
        new_interesting_field = ""
        new_user = module.User(uuid, new_git_nickname, new_interesting_field)
        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            return 0
        return 1
    def delete(self, uuid):
        try:
            user = module.User.query.filter_by(user_uuid=uuid).first()
            db.session.delete(user)
            db.session.commit()
        except:
            return 0
        return 1

@api.route('/gpttest/<string:uuid>')
class gpttest(Resource):
    def get(self, uuid):
        try:
            uuid = module.ItemSelfIntroduction.query.filter_by(script_item_uuid = uuid).first()
        except:
            return 0
        
        return uuid

if __name__ == "__main__":
    app.run(host = "0.0.0.0")

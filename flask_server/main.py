import sys, os
from flask import Flask, request, jsonify
import config
from database.db_connect import db
from database import module
from flask_restx import Resource, Api
from user_route import user_path

app = Flask(__name__) # app assignment
app.config.from_object(config) # app setting config through config object(related to DB)
db.init_app(app)
app.register_blueprint(user_path.user_ab, url_prefix='/user')

api = Api(app) # api that make restapi more easier

@api.route('/test/<string:uuid>')
class test(Resource):
    def get(self, uuid):
        return module.user_info_table.query.filter_by(user_uuid=uuid).first().git_nickname
    def post(self, uuid):
        data = request.get_json()
        return jsonify(data)

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
        new_git_nickname = request.get_json()['git_nickname']
        raw_interesting_list = request.get_json()['interesting_field']
        new_interesting_field = ""
        for interest_subject in raw_interesting_list:
            new_interesting_field += interest_subject + ','
        new_interesting_field = new_interesting_field[0:-1]
        new_user = module.User(uuid, new_git_nickname, new_interesting_field)
        try:
            db.session.add(new_user)
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

if __name__ == "__main__":
    app.run(host = "0.0.0.0")

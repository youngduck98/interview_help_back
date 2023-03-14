"""
this file is created to record the practical code
may be destroyed before submit
"""

from flask import Flask, request
from flask_restx import Resource, Api

#if you want to test the new config, then you can use this.
def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object(config)
    else:
        app.config.update(test_config)
		
    db.init_app(app)

app = Flask(__name__) # app assignment
api = Api(app) # api that make restapi more easier

@app.route('/')
def main_page_mesg():
    return "this is capstone main page\n"

@app.route('/today_question') #get echo api
def get_echo_call():
    today_list = "today_question"
    return today_list

@app.route('/user_interest_list', methods=['POST']) #test api
def user_interest_list():
    param = request.get_json()
    print(param)
    return jsonify(param)
    #return jsonify({"user_uuid": interest_list[0], "list" : interest_list[1:]})

todos = {}
count = 1

@api.route('/todos')
class TodoPost(Resource):
    def post(self):
        print("post\n   ")
        global count
        global todos

        idx = count
        count += 1
        todos[idx] = request.json.get('data')
        print(todos[idx])

        return {
            'todo_id': idx,
            'data': todos[idx]
        }

@api.route('/todos/<int:todo_id>')
class TodoSimple(Resource):
    def get(self, todo_id):
        return {
            'todo_id': todo_id,
            'data': todos[todo_id]
        }

    def put(self, todo_id):
        todos[todo_id] = request.json.get('data')
        return {
            'todo_id': todo_id,
            'data': todos[todo_id]
        }
    
    def delete(self, todo_id):
        del todos[todo_id]
        return {
            "delete" : "success"
        }

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
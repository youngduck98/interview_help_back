from flask import Flask, request, jsonify

app = Flask(__name__)

def search(a = 1, b = 2):
    return [a, b]

@app.route('/user_interest_list', methods=['POST']) #test api
def user_interest_list():
    param = request.get_json()
    print(param)
    return jsonify(param)
    #return jsonify({"user_uuid": interest_list[0], "list" : interest_list[1:]})

@app.route('/today_question', methods=['POST']) #get echo api
def get_echo_call():
    today_list = search(request.get_json()['user_uuid'])
    return today_list

@app.route('/attendance_checking', methods=['POST'])
def attd_check():
    answer = False
    #answer = query
    return answer

@app.route('/attendance_info', methods=['POST'])
def attendance_info():
    answer = False
    weak_attendance = search(request.get_json()['user_uuid'])
    return weak_attendance

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080')
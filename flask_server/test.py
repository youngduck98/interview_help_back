from flask import Flask, request

app = Flask(__name__) # app assignment

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

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
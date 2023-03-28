"""
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from database.module import User, Achievement, Attendance, CommonQue, IndividualQue, InterviewLog, InterviewQuestion, ItemSelfIntroduction, MockInterview, SynthesisSelfIntroduction

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

"\n\n1. Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?
\n2. Attention 메커니즘은 어떤 기능을 가지고 있는가?
\n3. Attention 메커니즘을 사용하면 어떤 이점이 있는가?"
"""

def parse_statment(s):
    ret1 = s.split("\n")
    while len(ret1) != 0 and ret1[0] == '':
        del ret1[0]
    for i in range(len(ret1)):
        if '. ' in ret1[i]:
            ret1[i] = ret1[i].split('. ')[1]
    return ret1
s = "\n\n1. Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?\n" + \
"2. Attention 메커니즘은 어떤 기능을 가지고 있는가?\n" + \
"3. Attention 메커니즘을 사용하면 어떤 이점이 있는가?"

s = parse_statment(s)
print(s)
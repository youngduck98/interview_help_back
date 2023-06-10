# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from .db_connect import db
from datetime import datetime
import pytz

class UserInfo(db.Model):
    __tablename__ = 'user_info'

    user_uuid = db.Column(db.String(45), primary_key=True, server_default=db.FetchedValue())
    git_nickname = db.Column(db.String(45), server_default=db.FetchedValue())
    
    def __init__(self, user_uuid, git_nickname):
        self.user_uuid = user_uuid
        self.git_nickname = git_nickname

class Attendance(db.Model):
    __tablename__ = 'Attendance'

    att_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    att_date = db.Column(db.DateTime, nullable=False)

    User = db.relationship('User', primaryjoin='Attendance.user_uuid == User.user_uuid', backref='attendances')

    def __init__(self, att_uuid, user_uuid, att_date = datetime.now(pytz.timezone('Asia/Seoul'))):
        self.att_uuid = att_uuid
        self.user_uuid = user_uuid
        self.att_date = att_date

class CommonQue(db.Model):
    __tablename__ = 'CommonQues'

    ques_uuid = db.Column(db.String(36), primary_key=True)
    question = db.Column(db.String(1000))
    ques_type = db.Column(db.Integer, server_default=db.FetchedValue())
    recommendation = db.Column(db.Integer, server_default=db.FetchedValue())
    
    def __init__(self, ques_uuid, question, ques_type=0, recommendation=0):
        self.ques_uuid = ques_uuid
        self.question = question
        self.ques_type = ques_type
        self.recommendation = recommendation

class IndividualQue(db.Model):
    __tablename__ = 'IndividualQues'

    ques_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    script_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), nullable=False, index=True)
    question = db.Column(db.String(1000))

    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='IndividualQue.script_uuid == SynthesisSelfIntroduction.script_uuid', backref='individual_ques')
    User = db.relationship('User', primaryjoin='IndividualQue.user_uuid == User.user_uuid', backref='individual_ques')

    def __init__(self, ques_uuid, user_uuid, script_uuid, question = ""):
        self.ques_uuid = ques_uuid
        self.user_uuid = user_uuid
        self.script_uuid = script_uuid
        self.question = question

class MockInterview(db.Model):
    __tablename__ = 'MockInterview'

    interview_uuid = db.Column(db.String(36), primary_key=True)
    interview_host_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    score = db.Column(db.Integer, server_default=db.FetchedValue())
    referenced_script = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), nullable=False, index=True)
    end_time = db.Column(db.DateTime)
    self_memo = db.Column(db.String(5000))
    total_duration = db.Column(db.Integer)

    User = db.relationship('User', primaryjoin='MockInterview.interview_host_uuid == User.user_uuid', backref='mock_interviews')
    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='MockInterview.referenced_script == SynthesisSelfIntroduction.script_uuid', backref='mock_interviews')

    def __init__(self, interview_uuid, interview_host_uuid, referenced_script, self_memo="", score = -1, endtime=datetime.now(pytz.timezone('Asia/Seoul'))):
        self.interview_uuid = interview_uuid
        self.interview_host_uuid = interview_host_uuid
        self.referenced_script = referenced_script
        self.end_time = endtime
        self.self_memo = self_memo
        self.score = score
        
class SelfIntroductionA(db.Model):
    __tablename__ = 'SelfIntroduction_A'

    script_ans_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    script_ques_uuid = db.Column(db.ForeignKey('SelfIntroduction_Q.script_ques_uuid'), nullable=False, index=True)
    answer = db.Column(db.String(5000))
    script_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), index=True)

    SelfIntroduction_Q = db.relationship('SelfIntroductionQ', primaryjoin='SelfIntroductionA.script_ques_uuid == SelfIntroductionQ.script_ques_uuid', backref='self_introduction_as')
    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='SelfIntroductionA.script_uuid == SynthesisSelfIntroduction.script_uuid', backref='self_introduction_as')
    User = db.relationship('User', primaryjoin='SelfIntroductionA.user_uuid == User.user_uuid', backref='self_introduction_as')

    def __init__(self, script_ans_uuid, user_uuid, script_ques_uuid, answer="", script_uuid=""):
        self.script_ans_uuid = script_ans_uuid
        self.user_uuid = user_uuid
        self.script_ques_uuid = script_ques_uuid
        self.answer = answer
        self.script_uuid = script_uuid

class SelfIntroductionQ(db.Model):
    __tablename__ = 'SelfIntroduction_Q'

    script_ques_uuid = db.Column(db.String(36), primary_key=True)
    question = db.Column(db.String(1000), nullable=False)
    index = db.Column(db.Integer)
    tip = db.Column(db.String(1500))
    max_answer_len = db.Column(db.Integer, server_default=db.FetchedValue())
    
    def __init__(self, script_ques_uuid, question, index=0, tip=""):
        self.script_ques_uuid = script_ques_uuid
        self.question = question
        self.index = index
        self.tip = tip

class SynthesisSelfIntroduction(db.Model):
    __tablename__ = 'SynthesisSelfIntroduction'

    script_uuid = db.Column(db.String(45), primary_key=True)
    script_host = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    script_date = db.Column(db.DateTime, nullable=False)
    script_title = db.Column(db.String(45), nullable=False)
    question = db.Column(db.String(200))
    interview = db.Column(db.Integer, server_default=db.FetchedValue())
    objective = db.Column(db.ForeignKey('job_object_field.object_type'), index=True, server_default=db.FetchedValue())
    interview_ready = db.Column(db.Integer, server_default=db.FetchedValue())
    
    job_object_field = db.relationship('JobObjectField', primaryjoin='SynthesisSelfIntroduction.objective == JobObjectField.object_type', backref='synthesis_self_introductions')
    User = db.relationship('User', primaryjoin='SynthesisSelfIntroduction.script_host == User.user_uuid', backref='synthesis_self_introductions')

    def __init__(self, script_uuid, script_host, script_date, script_title, question="", used=0, objective=0, interview_ready=0):
        self.script_uuid = script_uuid
        self.script_host = script_host
        self.script_date = script_date
        self.script_title = script_title
        self.question = question
        self.interview = used
        self.objective = objective
        self.interview_ready = interview_ready
        
class TodayQue(db.Model):
    __tablename__ = 'TodayQues'

    tq_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    today_ques = db.Column(db.ForeignKey('CommonQues.ques_uuid'), nullable=False, index=True)
    user_memo = db.Column(db.String(800))
    date = db.Column(db.DateTime)

    CommonQue = db.relationship('CommonQue', primaryjoin='TodayQue.today_ques == CommonQue.ques_uuid', backref='today_ques')
    User = db.relationship('User', primaryjoin='TodayQue.user_uuid == User.user_uuid', backref='today_ques')
    
    def __init__(self, tq_uuid, user_uuid, today_ques, user_memo="", date=datetime.now(pytz.timezone('Asia/Seoul'))):
        self.tq_uuid = tq_uuid
        self.user_uuid = user_uuid
        self.today_ques =today_ques
        self.user_memo = user_memo
        self.date = date
        
class User(db.Model):
    __tablename__ = 'User'

    user_uuid = db.Column(db.String(36), primary_key=True)
    git_nickname = db.Column(db.String(200))
    interesting_field = db.Column(db.String(1000))
    name = db.Column(db.String(100))
    email = db.Column(db.String(200))
    att_continue = db.Column(db.Integer, server_default=db.FetchedValue())
    
    def __init__(self, user_uuid, git_nickname, interesting_field, name, email, att_continue=0):
        self.user_uuid = user_uuid
        self.git_nickname = git_nickname
        self.interesting_field = interesting_field
        self.name = name
        self.email = email
        self.att_continue = att_continue

class CommunityComment(db.Model):
    __tablename__ = 'community_comment'

    cc_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    common_ques = db.Column(db.ForeignKey('CommonQues.ques_uuid'), nullable=False, index=True)
    comment = db.Column(db.String(5000), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    recommendation = db.Column(db.Integer, server_default=db.FetchedValue())

    CommonQue = db.relationship('CommonQue', primaryjoin='CommunityComment.common_ques == CommonQue.ques_uuid', backref='community_comments')
    User = db.relationship('User', primaryjoin='CommunityComment.user_uuid == User.user_uuid', backref='community_comments')

    def __init__(self, cc_uuid, user_uuid, common_ques, comment, date=datetime.now(pytz.timezone('Asia/Seoul')), recommendation=0):
        self.cc_uuid = cc_uuid
        self.user_uuid = user_uuid
        self.common_ques = common_ques
        self.comment = comment
        self.date = date
        self.recommendation = recommendation

class CommentRecommendation(db.Model):
    __tablename__ = 'comment_recommendation'

    cr_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    cc_uuid = db.Column(db.ForeignKey('community_comment.cc_uuid'), nullable=False, index=True)
    
    User = db.relationship('User', primaryjoin='CommentRecommendation.user_uuid == User.user_uuid', backref='comment_recommendations')
    
    def __init__(self, cr_uuid, user_uuid, cc_uuid):
        self.cr_uuid = cr_uuid
        self.user_uuid = user_uuid
        self.cc_uuid = cc_uuid

class InterviewQuesCommon(db.Model):
    __tablename__ = 'interview_ques_common'

    common_meta_uuid = db.Column(db.String(36), primary_key=True)
    interview_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), nullable=False, index=True)
    common_ques_uuid = db.Column(db.ForeignKey('CommonQues.ques_uuid'), nullable=False, index=True)
    index = db.Column(db.Integer, server_default=db.FetchedValue())
    
    CommonQue = db.relationship('CommonQue', primaryjoin='InterviewQuesCommon.common_ques_uuid == CommonQue.ques_uuid', backref='interview_ques_commons')
    MockInterview = db.relationship('MockInterview', primaryjoin='InterviewQuesCommon.interview_uuid == MockInterview.interview_uuid', backref='interview_ques_commons')

    def __init__(self, common_meta_uuid, interview_uuid, common_ques_uuid, index=0):
        self.common_meta_uuid = common_meta_uuid
        self.interview_uuid = interview_uuid
        self.common_ques_uuid = common_ques_uuid
        self.index = index

class InterviewQuesIndividual(db.Model):
    __tablename__ = 'interview_ques_Individual'

    indiv_meta_uuid = db.Column(db.String(36), primary_key=True)
    interview_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), nullable=False, index=True)
    indiv_ques_uuid = db.Column(db.ForeignKey('IndividualQues.ques_uuid'), nullable=False, index=True)
    index = db.Column(db.Integer, server_default=db.FetchedValue())
    
    IndividualQue = db.relationship('IndividualQue', primaryjoin='InterviewQuesIndividual.indiv_ques_uuid == IndividualQue.ques_uuid', backref='interview_ques_individuals')
    MockInterview = db.relationship('MockInterview', primaryjoin='InterviewQuesIndividual.interview_uuid == MockInterview.interview_uuid', backref='interview_ques_individuals')
    
    def __init__(self, indiv_meta_uuid, interview_uuid, indiv_ques_uuid, index):
        self.indiv_meta_uuid = indiv_meta_uuid
        self.interview_uuid = interview_uuid
        self.indiv_ques_uuid = indiv_ques_uuid
        self.index = index

class JobObjectField(db.Model):
    __tablename__ = 'job_object_field'

    object_type = db.Column(db.Integer, primary_key=True, unique=True)
    object_name = db.Column(db.String(45), unique=True)

class InterestOptionField(db.Model):
    __tablename__ = 'interest_option_field'

    type = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(45), unique=True)
    
class UserInterest(db.Model):
    __tablename__ = 'user_interest'
    user_uuid = db.Column(db.String(36), db.ForeignKey('User.user_uuid'), primary_key=True, nullable=False, index=True)
    interest_type = db.Column(db.Integer, db.ForeignKey('interest_option_field.type'), primary_key=True, nullable=False, index=True)
    
    def __init__(self, user_uuid, interest_type):
        self.user_uuid = user_uuid
        self.interest_type = interest_type

class AnsScore(db.Model):
    __tablename__ = 'ans_score'

    as_uuid = db.Column(db.String(36), primary_key=True)
    interview_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), index=True)
    question = db.Column(db.String(1000))
    answer = db.Column(db.String(10000))
    feedback = db.Column(db.String(5000))
    score = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    index = db.Column(db.Integer, server_default=db.FetchedValue())
    duration_warning = db.Column(db.Integer)
    
    MockInterview = db.relationship('MockInterview', \
        primaryjoin='AnsScore.interview_uuid == MockInterview.interview_uuid', backref='ans_scores')
    
    def __init__(self, as_uuid, interview_uuid, question, answer, feedback, \
        score, duration, index=0, duration_warning=0):
        self.as_uuid = as_uuid
        self.interview_uuid = interview_uuid
        self.question = question
        self.answer = answer
        self.feedback = feedback
        self.score = score
        self.duration = duration
        self.index = index
        self.duration_warning = duration_warning
    
class BadExpression(db.Model):
    __tablename__ = 'bad_expression'

    be_uuid = db.Column(db.String(36), primary_key=True)
    interview_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), index=True)
    expression = db.Column(db.String(45))
    num = db.Column(db.Integer)

    MockInterview = db.relationship('MockInterview', \
        primaryjoin='BadExpression.interview_uuid == MockInterview.interview_uuid', \
            backref='bad_expressions')
    
    def __init__(self, be_uuid, interview_uuid, expression, num=0):
        self.be_uuid = be_uuid
        self.interview_uuid = interview_uuid
        self.expression = expression
        self.num = num
    
class BadPose(db.Model):
    __tablename__ = 'bad_pose'

    bp_uuid = db.Column(db.String(36), primary_key=True)
    interview_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), index=True)
    pose = db.Column(db.String(45))
    num = db.Column(db.String(45))

    MockInterview = db.relationship('MockInterview', \
        primaryjoin='BadPose.interview_uuid == MockInterview.interview_uuid',\
            backref='bad_poses')
    
    def __init__(self, bp_uuid, interview_uuid, pose, num=0):
        self.bp_uuid = bp_uuid
        self.interview_uuid = interview_uuid
        self.pose = pose
        self.num = num

class InterestObjectRelation(db.Model):
    __tablename__ = 'interest_object_relation'
    
    interest_type = db.Column(db.Integer, db.ForeignKey('interest_option_field.type'), \
        primary_key=True, nullable=False, index=True)
    object_type = db.Column(db.Integer, db.ForeignKey('job_object_field'), \
        primary_key=True, nullable=False, index=True)
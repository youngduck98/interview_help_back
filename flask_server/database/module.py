# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from .db_connect import db
from datetime import datetime
import pytz

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
    recommandation = db.Column(db.Integer, server_default=db.FetchedValue())
    
    def __init__(self, ques_uuid, question, ques_type=0, recommandation=0):
        self.ques_uuid = ques_uuid
        self.question = question
        self.ques_type = ques_type
        self.recommandation = recommandation

class IndividualQue(db.Model):
    __tablename__ = 'IndividualQues'

    ques_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    script_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), nullable=False, index=True)

    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='IndividualQue.script_uuid == SynthesisSelfIntroduction.script_uuid', backref='individual_ques')
    User = db.relationship('User', primaryjoin='IndividualQue.user_uuid == User.user_uuid', backref='individual_ques')
    
    def __init__(self, ques_uuid, user_uuid, script_uuid):
        self.ques_uuid = ques_uuid
        self.user_uuid = user_uuid
        self.script_uuid = script_uuid

class MockInterview(db.Model):
    __tablename__ = 'MockInterview'

    interview_uuid = db.Column(db.String(36), primary_key=True)
    interview_host_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    score = db.Column(db.Integer, server_default=db.FetchedValue())
    referenced_script = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), nullable=False, index=True)
    individual_question1 = db.Column(db.ForeignKey('IndividualQues.ques_uuid'), index=True)
    individual_question2 = db.Column(db.ForeignKey('IndividualQues.ques_uuid'), index=True)
    common_question1 = db.Column(db.ForeignKey('CommonQues.ques_uuid'), index=True)
    common_question2 = db.Column(db.ForeignKey('CommonQues.ques_uuid'), index=True)
    common_question3 = db.Column(db.ForeignKey('CommonQues.ques_uuid'), index=True)
    end_time = db.Column(db.DateTime)
    self_memo = db.Column(db.String(5000))
        
    CommonQue = db.relationship('CommonQue', primaryjoin='MockInterview.common_question1 == CommonQue.ques_uuid', backref='commonque_commonque_mock_interviews')
    CommonQue1 = db.relationship('CommonQue', primaryjoin='MockInterview.common_question2 == CommonQue.ques_uuid', backref='commonque_commonque_mock_interviews_0')
    CommonQue2 = db.relationship('CommonQue', primaryjoin='MockInterview.common_question3 == CommonQue.ques_uuid', backref='commonque_commonque_mock_interviews')
    IndividualQue = db.relationship('IndividualQue', primaryjoin='MockInterview.individual_question1 == IndividualQue.ques_uuid', backref='individualque_mock_interviews')
    IndividualQue1 = db.relationship('IndividualQue', primaryjoin='MockInterview.individual_question2 == IndividualQue.ques_uuid', backref='individualque_mock_interviews_0')
    User = db.relationship('User', primaryjoin='MockInterview.interview_host_uuid == User.user_uuid', backref='mock_interviews')
    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='MockInterview.referenced_script == SynthesisSelfIntroduction.script_uuid', backref='mock_interviews')
    
    def __init__(self, interview_uuid, interview_host_uuid, referenced_script, self_memo="", iq1=None, cq1=None, cq2=None, iq2=None, cq3=None, endtime=datetime.now(pytz.timezone('Asia/Seoul'))):
        self.interview_uuid = interview_uuid
        self.interview_host_uuid = interview_host_uuid
        self.referenced_script = referenced_script
        self.individual_question1 = iq1
        self.individual_question2 = iq2
        self.common_question1 = cq1
        self.common_question2 = cq2
        self.common_question3 = cq3
        self.end_time = endtime
        self.self_memo = self_memo
    
class SelfIntroductionA(db.Model):
    __tablename__ = 'SelfIntroduction_A'

    script_ans_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    script_ques_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), nullable=False, index=True)
    answer = db.Column(db.String(5000))

    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='SelfIntroductionA.script_ques_uuid == SynthesisSelfIntroduction.script_uuid', backref='self_introduction_as')
    User = db.relationship('User', primaryjoin='SelfIntroductionA.user_uuid == User.user_uuid', backref='self_introduction_as')
    
    def __init__(self, script_ans_uuid, user_uuid, script_ques_uuid, answer=""):
        self.script_ans_uuid = script_ans_uuid
        self.user_uuid = user_uuid
        self.script_ques_uuid = script_ques_uuid
        self.answer = answer



class SelfIntroductionQ(db.Model):
    __tablename__ = 'SelfIntroduction_Q'

    script_ques_uuid = db.Column(db.String(36), primary_key=True)
    question = db.Column(db.String(1000), nullable=False)
    index = db.Column(db.Integer)
    tip = db.Column(db.String(1500))
    
    def __init__(self, script_ques_uuid, question, index=0, tip=""):
        self.script_ques_uuid = script_ques_uuid
        self.question = question
        self.index = index
        self.tip = tip



class SynthesisSelfIntroduction(db.Model):
    __tablename__ = 'SynthesisSelfIntroduction'

    script_uuid = db.Column(db.String(45), primary_key=True)
    script_host = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    script_date = db.Column(db.String(45), nullable=False)
    script_title = db.Column(db.String(45), nullable=False)
    question = db.Column(db.String(200))
    
    User = db.relationship('User', primaryjoin='SynthesisSelfIntroduction.script_host == User.user_uuid', backref='synthesis_self_introductions')
    
    def __init__(self, script_uuid, script_host, script_date, script_title, question=""):
        self.script_uuid = script_uuid
        self.script_host = script_host
        self.script_date = script_date
        self.script_title = script_title
        self.question = question
        
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
    
    def __init__(self, user_uuid, git_nickname, name, email, att_continue=0):
        self.user_uuid = user_uuid
        self.git_nickname = git_nickname
        self.name = name
        self.email = email
        self.att_continue = att_continue

class CommentRecommandation(db.Model):
    __tablename__ = 'comment_recommandation'

    cr_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)

    User = db.relationship('User', primaryjoin='CommentRecommandation.user_uuid == User.user_uuid', backref='comment_recommandations')
    
    def __init__(self, cr_uuid, user_uuid):
        self.cr_uuid = cr_uuid
        self.user_uuid = user_uuid

class CommunityComment(db.Model):
    __tablename__ = 'community_comment'

    cc_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    common_ques = db.Column(db.ForeignKey('CommonQues.ques_uuid'), nullable=False, index=True)
    comment = db.Column(db.String(5000), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    recommandation = db.Column(db.Integer, server_default=db.FetchedValue())

    CommonQue = db.relationship('CommonQue', primaryjoin='CommunityComment.common_ques == CommonQue.ques_uuid', backref='community_comments')
    User = db.relationship('User', primaryjoin='CommunityComment.user_uuid == User.user_uuid', backref='community_comments')

    def __init__(self, cc_uuid, user_uuid, common_ques, comment, date=datetime.now(pytz.timezone('Asia/Seoul')), recommandation=0):
        self.cc_uuid = cc_uuid
        self.user_uuid = user_uuid
        self.common_ques = common_ques
        self.comment = comment
        self.date = date
        self.recommandation = recommandation
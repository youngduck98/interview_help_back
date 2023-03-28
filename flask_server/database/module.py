# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from .db_connect import db
from datetime import datetime

class Achievement(db.Model):
    __tablename__ = 'Achievement'

    achi_uuid = db.Column(db.String(36), primary_key=True)
    host_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    achi_type = db.Column(db.Integer)
    achi_text = db.Column(db.String(200))
    date = db.Column(db.BigInteger)

    User = db.relationship('User', primaryjoin='Achievement.host_uuid == User.user_uuid', backref='achievements')



class Attendance(db.Model):
    __tablename__ = 'Attendance'

    att_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    att_continuity = db.Column(db.Integer)
    att_date = db.Column(db.DateTime)

    User = db.relationship('User', primaryjoin='Attendance.user_uuid == User.user_uuid', backref='attendances')
    
    def __init__(self, att_uuid, user_uuid, att_continuity, att_date):
        self.att_uuid = att_uuid
        self.user_uuid = user_uuid
        self.att_continuity = att_continuity
        self.att_date = att_date


class CommonQue(db.Model):
    __tablename__ = 'CommonQues'

    ques_uuid = db.Column(db.String(36), primary_key=True)
    contents = db.Column(db.String(1000))
    ques_type = db.Column(db.Integer)



class IndividualQue(db.Model):
    __tablename__ = 'IndividualQues'

    ques_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), nullable=False, index=True)
    script_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), nullable=False, index=True)

    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='IndividualQue.script_uuid == SynthesisSelfIntroduction.script_uuid', backref='individual_ques')
    User = db.relationship('User', primaryjoin='IndividualQue.user_uuid == User.user_uuid', backref='individual_ques')



class InterviewLog(db.Model):
    __tablename__ = 'InterviewLog'

    log_uuid = db.Column(db.String(36), primary_key=True)
    inter_ques_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), index=True)
    log_date = db.Column(db.DateTime)
    log_content = db.Column(db.String(1000))
    log_type = db.Column(db.Integer)
    log_progress = db.Column(db.Integer)

    MockInterview = db.relationship('MockInterview', primaryjoin='InterviewLog.inter_ques_uuid == MockInterview.interview_uuid', backref='interview_logs')



class InterviewQuestion(db.Model):
    __tablename__ = 'InterviewQuestion'

    inter_ques_uuid = db.Column(db.String(36), primary_key=True)
    interview_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), index=True)
    common_question_uuid = db.Column(db.ForeignKey('CommonQues.ques_uuid'), index=True)
    indiv_ques_uuid = db.Column(db.String(36))
    type = db.Column(db.Integer)

    CommonQue = db.relationship('CommonQue', primaryjoin='InterviewQuestion.common_question_uuid == CommonQue.ques_uuid', backref='interview_questions')
    MockInterview = db.relationship('MockInterview', primaryjoin='InterviewQuestion.interview_uuid == MockInterview.interview_uuid', backref='interview_questions')



class ItemSelfIntroduction(db.Model):
    __tablename__ = 'ItemSelfIntroduction'

    script_item_uuid = db.Column(db.String(36), primary_key=True)
    script_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), index=True)
    question = db.Column(db.String(1000))
    contents = db.Column(db.String(5000))
    index = db.Column(db.Integer)

    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='ItemSelfIntroduction.script_uuid == SynthesisSelfIntroduction.script_uuid', backref='item_self_introductions')



class MockInterview(db.Model):
    __tablename__ = 'MockInterview'

    interview_uuid = db.Column(db.String(36), primary_key=True)
    interview_host_uuid = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    referenced_script = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), index=True)
    score = db.Column(db.Integer)
    end_time = db.Column(db.DateTime)
    self_memo = db.Column(db.String(5000))

    User = db.relationship('User', primaryjoin='MockInterview.interview_host_uuid == User.user_uuid', backref='mock_interviews')
    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='MockInterview.referenced_script == SynthesisSelfIntroduction.script_uuid', backref='mock_interviews')



class SynthesisSelfIntroduction(db.Model):
    __tablename__ = 'SynthesisSelfIntroduction'

    script_uuid = db.Column(db.String(36), primary_key=True)
    script_host = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    script_date = db.Column(db.DateTime)
    script_title = db.Column(db.String(200))

    User = db.relationship('User', primaryjoin='SynthesisSelfIntroduction.script_host == User.user_uuid', backref='synthesis_self_introductions')



class TodayQue(db.Model):
    __tablename__ = 'TodayQues'

    tq_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    today_ques = db.Column(db.ForeignKey('CommonQues.ques_uuid'), index=True)
    user_memo = db.Column(db.String(800))
    date = db.Column(db.DateTime)

    CommonQue = db.relationship('CommonQue', primaryjoin='TodayQue.today_ques == CommonQue.ques_uuid', backref='today_ques')
    User = db.relationship('User', primaryjoin='TodayQue.user_uuid == User.user_uuid', backref='today_ques')



class User(db.Model):
    __tablename__ = 'User'

    user_uuid = db.Column(db.String(36), primary_key=True)
    git_nickname = db.Column(db.String(200))
    interesting_field = db.Column(db.String(1000))
    name = db.Column(db.String(100))
    email = db.Column(db.String(200))
    att_continue = db.Column(db.Integer, server_default=db.FetchedValue())
        
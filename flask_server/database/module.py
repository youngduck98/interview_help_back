from .db_connect import db

class user_info_table(db.Model):
    __tablename__ = "user_info"

    user_uuid = db.Column(db.Integer, primary_key=True)
    git_nickname = db.Column(db.String(45))

class Achievement(db.Model):
    __tablename__ = 'Achievement'

    achi_uuid = db.Column(db.String(36), primary_key=True)
    host_uuid = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    achi_type = db.Column(db.Integer)
    achi_text = db.Column(db.String(200))
    date = db.Column(db.BigInteger)

    User = db.relationship('User', primaryjoin='Achievement.host_uuid == User.user_uuid', backref='achievements')



class Attendance(db.Model):
    __tablename__ = 'Attendance'

    att_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    att_point = db.Column(db.Integer)
    att_continuity = db.Column(db.Integer)
    att_date = db.Column(db.BigInteger)
    att_question = db.Column(db.ForeignKey('IndividualQues.ques_uuid'), index=True)

    IndividualQue = db.relationship('IndividualQue', primaryjoin='Attendance.att_question == IndividualQue.ques_uuid', backref='attendances')
    User = db.relationship('User', primaryjoin='Attendance.user_uuid == User.user_uuid', backref='attendances')



class CommonQue(db.Model):
    __tablename__ = 'CommonQues'

    ques_uuid = db.Column(db.String(36), primary_key=True)
    contents = db.Column(db.String(1000))
    ques_type = db.Column(db.Integer)



class IndividualQue(db.Model):
    __tablename__ = 'IndividualQues'

    ques_uuid = db.Column(db.String(36), primary_key=True)
    user_uuid = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    script_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), index=True)

    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='IndividualQue.script_uuid == SynthesisSelfIntroduction.script_uuid', backref='individual_ques')
    User = db.relationship('User', primaryjoin='IndividualQue.user_uuid == User.user_uuid', backref='individual_ques')



class InterviewLog(db.Model):
    __tablename__ = 'InterviewLog'

    log_uuid = db.Column(db.String(36), primary_key=True)
    inter_ques_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), index=True)
    log_date = db.Column(db.BigInteger)
    log_content = db.Column(db.String(1000))
    log_type = db.Column(db.Integer)
    log_progress = db.Column(db.Integer)

    MockInterview = db.relationship('MockInterview', primaryjoin='InterviewLog.inter_ques_uuid == MockInterview.interview_uuid', backref='interview_logs')



class InterviewQuestion(db.Model):
    __tablename__ = 'InterviewQuestion'

    inter_ques_uuid = db.Column(db.String(36), primary_key=True)
    interview_uuid = db.Column(db.ForeignKey('MockInterview.interview_uuid'), db.ForeignKey('IndividualQues.ques_uuid'), index=True)
    common_question_uuid = db.Column(db.ForeignKey('CommonQues.ques_uuid'), index=True)
    indiv_ques_uuid = db.Column(db.String(36))
    type = db.Column(db.Integer)

    CommonQue = db.relationship('CommonQue', primaryjoin='InterviewQuestion.common_question_uuid == CommonQue.ques_uuid', backref='interview_questions')
    IndividualQue = db.relationship('IndividualQue', primaryjoin='InterviewQuestion.interview_uuid == IndividualQue.ques_uuid', backref='interview_questions')
    MockInterview = db.relationship('MockInterview', primaryjoin='InterviewQuestion.interview_uuid == MockInterview.interview_uuid', backref='interview_questions')



class ItemSelfIntroduction(db.Model):
    __tablename__ = 'ItemSelfIntroduction'

    script_item_uuid = db.Column(db.String(36), primary_key=True)
    script_uuid = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), index=True)
    contents = db.Column(db.String(5000))
    index = db.Column(db.Integer)

    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='ItemSelfIntroduction.script_uuid == SynthesisSelfIntroduction.script_uuid', backref='item_self_introductions')



class MockInterview(db.Model):
    __tablename__ = 'MockInterview'

    interview_uuid = db.Column(db.String(36), primary_key=True)
    interview_host_uuid = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    score = db.Column(db.Integer)
    referenced_script = db.Column(db.ForeignKey('SynthesisSelfIntroduction.script_uuid'), index=True)
    end_time = db.Column(db.BigInteger)
    self_memo = db.Column(db.String(5000))

    User = db.relationship('User', primaryjoin='MockInterview.interview_host_uuid == User.user_uuid', backref='mock_interviews')
    SynthesisSelfIntroduction = db.relationship('SynthesisSelfIntroduction', primaryjoin='MockInterview.referenced_script == SynthesisSelfIntroduction.script_uuid', backref='mock_interviews')



class SynthesisSelfIntroduction(db.Model):
    __tablename__ = 'SynthesisSelfIntroduction'

    script_uuid = db.Column(db.String(36), primary_key=True)
    script_host = db.Column(db.ForeignKey('User.user_uuid'), index=True)
    script_date = db.Column(db.BigInteger)
    script_name = db.Column(db.String(200))

    User = db.relationship('User', primaryjoin='SynthesisSelfIntroduction.script_host == User.user_uuid', backref='synthesis_self_introductions')



class User(db.Model):
    __tablename__ = 'User'

    user_uuid = db.Column(db.String(36), primary_key=True)
    git_nickname = db.Column(db.String(200))
    interesting_field = db.Column(db.String(1000))
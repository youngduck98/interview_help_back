 # -*- coding: utf8 -*-
from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.expression import func
from flask_restx import Resource, Api
from database.db_connect import db
from database.module import Attendance, CommonQue, IndividualQue, MockInterview, \
    SelfIntroductionA, SelfIntroductionQ, SynthesisSelfIntroduction, TodayQue, \
    User, CommentRecommendation, CommunityComment, InterviewQuesCommon, InterviewQuesIndividual, \
    BadPose, BadExpression, AnsScore, InterestObjectRelation
from database.list import default_interest_list
from database.dictionary import ques_type_dict
from function.about_time import date_return, turn_datetime_to_longint, today_return
from datetime import datetime, timedelta, date, timezone
from question.scoring import ScoreAns
import pytz, uuid, json, random
import time
from question.generate import GenerateQues

interview_ab = Blueprint('interview', __name__)
api = Api(interview_ab) # api that make restapi more easier

@api.route('/main/')
class interview_main(Resource):
    def get(self):
        return "interview_main"

def make_indivisual_ques(user_uuid:str, script_uuid:str, ques_num:int):
    ques_uuid_list = SynthesisSelfIntroduction.query.get(script_uuid).question.split(',')
    question = []
    answer = []
    
    try:
        for ques_uuid in ques_uuid_list:
            question.append(SelfIntroductionQ.query.get(ques_uuid).question)
            answer.append(SelfIntroductionA.query.filter(SelfIntroductionA.script_ques_uuid == ques_uuid, \
                SelfIntroductionA.user_uuid == user_uuid, SelfIntroductionA.script_uuid == script_uuid).first().answer)
        print(question)
        print(answer)
        ret = GenerateQues(contents_q=question, contents_a=answer, num_pairs= ques_num).genQues()
        print("genque_end")
        for i in range(ques_num):
            db.session.add(IndividualQue(uuid.uuid1(), user_uuid, script_uuid, ret[i]))
        db.session.commit()
    except:
        print("false")
        return False
    return True

def make_individual(script_uuid:str, host_uuid:str):
    record = SynthesisSelfIntroduction.query.get(script_uuid)
    state = False
    print("start to make question")
    print("make_individual")
    print(host_uuid)
    print(script_uuid)
    record.interview_ready = 0
    while not state :
        state = make_indivisual_ques(host_uuid, script_uuid, 2)
    record.interview_ready = 1
    db.session.commit()
    print("end to make question")

def select_common_from_types(raw_interest_type_list):
    common_que_record = []
    
    #select common_que
    records = CommonQue.query.filter(CommonQue.ques_type == 0).order_by(func.random())
    if(len(raw_interest_type_list) > 1):
        for i in range(3):
            print("make common")
            selected_type = raw_interest_type_list[\
                int(random.randrange(0, len(raw_interest_type_list)))]
            records = CommonQue.query.filter(CommonQue.ques_type == selected_type).\
                order_by(func.random())
            offset = 0
            new_q = records.offset(offset).first()
            while(new_q in common_que_record):
                new_q = records.offset(offset).first()
                offset+=1
            if(not new_q):
                new_q = CommonQue.query.filter(CommonQue.ques_type == 0).order_by(func.random()).first()
            common_que_record.append(new_q)
    else:
        for i in range(3):
            print("make common")
            offset = 0
            new_q = records.offset(offset).first()
            while(not new_q or new_q in common_que_record):
                new_q = records.offset(offset).first()
                offset+=1
                if(not new_q):
                    new_q = CommonQue.query.filter(CommonQue.ques_type == 0).order_by(func.random()).first()
            common_que_record.append(new_q)
    print("end")
    return common_que_record

def role_to_type_list(role):
    records = InterestObjectRelation.query.filter(InterestObjectRelation.object_type == role).all()
    ret = [x.interest_type for x in records]
    return ret

class questionnare:
    def __init__(self, questionnaire_uuid, questions):
        self.questionnaire_uuid = questionnaire_uuid
        self.questions = questions

class InterviewQuestion:
    def __init__(self, question_uuid, question, ques_type):
        self.question_uuid = question_uuid
        self.question = question
        self.ques_type = ques_type
    
class InterviewData:
    def __init__(self, questionnaireUUID, badExpressions, badPose, progress, answers, durations):
        self.questionnaireUUID = questionnaireUUID
        self.badExpressions = badExpressions
        self.badPose = badPose
        self.progress = progress
        self.answers = answers
        self.durations = durations

class InterviewResult:
    def __init__(self, interviewUUID, interviewDate, rank, badPoses, badExpressions, \
        totalDuration, feedbackList):
        self.interviewUUID = interviewUUID
        self.interviewDate = interviewDate
        self.rank = rank
        self.badPoses = badPoses
        self.badExpressions = badExpressions
        self.totalDuration = totalDuration
        self.feedbackList = feedbackList

class FeedbackItem:
    def __init__(self, question, answer, feedback, duration, durationWarning):
        self.question = question
        self.answer = answer
        self.feedback = feedback
        self.duration = duration
        self.durationWarning = durationWarning

class AnswerItem:
    def __init__(self, answerUUID, questionUUID, answer):
        self.answerUUID = answerUUID
        self.questionUUID = questionUUID
        self.answer = answer

@api.route('/interview_questionnaire/')
class interview_questionnare(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        script_uuid = request.args.get('script_uuid')
        reuse = int(request.args.get('reuse'))
        print("reuse:", reuse)
        
        script_record = SynthesisSelfIntroduction.query.get(script_uuid)
        
        if(not script_record):
            print("no record")
            script_record = SynthesisSelfIntroduction.query.order_by(SynthesisSelfIntroduction.script_date.desc()).first()
            script_uuid = script_record.script_uuid
            return None
        elif(script_record.script_host != user_uuid):
            print("not match host")
            return None
        elif(script_record.interview_ready == 0 or reuse == 0):
            print("script_uuid", script_uuid)
            make_individual(script_uuid, user_uuid)
        job_object = script_record.objective
        ques_type = role_to_type_list(job_object)
        
        ready_record = SynthesisSelfIntroduction.query.get(script_uuid)
        if not ready_record:
            print("no script uuid such", script_uuid)
            return None
        print("why?")
        """
        while(ready_record.interview_ready == 0):
            time.sleep(0.5)
        """
        
        if(reuse == 1):
            interview_record = MockInterview.query.filter(MockInterview.referenced_script == \
                script_uuid, MockInterview.score != -1).order_by(MockInterview.end_time.desc()).first()
            interview_uuid = interview_record.interview_uuid
            if not interview_record:
                print("no interview record")
                return None
            else:
                interview_record.end_time = datetime.now(pytz.timezone('Asia/Seoul'))
        elif(reuse == 0):
            interview_uuid = uuid.uuid1()
        else:
            print("no reuse type")
            return None
        
        if reuse == 0:
            print("reuse = 0")
            common_que_records = select_common_from_types(ques_type)
            print("step 1.5")
            indiv_que_records = IndividualQue.query.filter(IndividualQue.script_uuid == script_uuid).\
                order_by(func.random()).limit(2).all()
            print("step 1")
            interview = MockInterview(interview_uuid, user_uuid, script_uuid)
            print("step 2")
            db.session.add(interview)
            print("step 3")
        
            index = 1
            print(len(common_que_records))
            print(len(indiv_que_records))
            if(len(indiv_que_records) < 2):
                make_individual(script_uuid, user_uuid)
                indiv_que_records = IndividualQue.query.filter(IndividualQue.script_uuid == script_uuid).\
                order_by(func.random()).limit(2).all()
        
            for record in common_que_records:
                print(type(record))
                IC_record = InterviewQuesCommon(uuid.uuid4(), interview_uuid, \
                        record.ques_uuid, index)
                index+=1
                db.session.add(IC_record)
            db.session.commit()
        
            for record in indiv_que_records:
                II_record = InterviewQuesIndividual(uuid.uuid4(), interview_uuid, \
                    record.ques_uuid, index)
                index+=1
                db.session.add(II_record)
            db.session.commit()
        index = 0
        
        print("interview_uuid:")
        print(interview_uuid)
        
        interview_record = MockInterview.query.get(interview_uuid)
        questionnare_script_record = SynthesisSelfIntroduction.query.\
            get(interview_record.referenced_script)
        if(interview_record.score == -1):
            interview_record.score = -2
            questionnare_script_record.interview = 1
            db.session.commit()
        
        common_uuid_list = [record.common_ques_uuid for record in InterviewQuesCommon.query.\
            filter(InterviewQuesCommon.interview_uuid == interview_uuid).limit(3).all()]
        
        indiv_uuid_list = [record.indiv_ques_uuid for record in InterviewQuesIndividual.query.\
            filter(InterviewQuesIndividual.interview_uuid == interview_uuid).limit(2).all()]
        ques_list = []
        
        print("insert, common_uuid_list, indiv_uuid_list")
        print(common_uuid_list)
        print(indiv_uuid_list)
    
        for uuidf in common_uuid_list:
            ques_list.append(InterviewQuestion(uuidf, CommonQue.query.get(uuidf).question, 0).__dict__)
        
        for uuidf in indiv_uuid_list:
            ques_list.append(InterviewQuestion(uuidf, IndividualQue.query.get(uuidf).question, 1).__dict__)
            
        try:
            print(questionnare(interview_uuid, ques_list).__dict__)
        except:
            pass
        
        return jsonify(questionnare(interview_uuid, ques_list).__dict__)
        

emotion_type = ["분노", "역겨움", "공포", "슬픔"]
pose_type = ["불필요한 얼굴 터치", "불안정한 자세(비대칭)"]

class InterviewResult:
    def __init__(self, interviewUUID, interviewDate, rank, badPoses, \
        badExpressions, totalDuration, feedbackList=""):
        self.interviewUUID = interviewUUID
        self.interviewDate = interviewDate
        self.rank = rank
        self.badPoses = badPoses
        self.badExpressions = badExpressions
        self.totalDuration = totalDuration
        self.feedbackList = feedbackList
        
class FeedbackItem:
    def __init__(self, question, answer, feedback, duration, durationWarning):
        self.question = question
        self.answer = answer
        self.feedback = feedback
        self.duration = duration
        self.durationWarning = durationWarning

def fake_scoring(ques_list, ans_list):
    score = [1,2,3,4,5]
    feedback = ["a", "b", "c", "d", "e"]
    return score, feedback

def fake_ranking(score, max_score=50, good_score=25):
    if(score >= good_score):
        return 'S'
    middle_score = int((good_score - score)/good_score * 5)
    return chr(65 + middle_score)

fake_duration_standard = 2

def return_interview_result(interview_uuid):
    interview_record = MockInterview.query.get(interview_uuid)
    bp_records = BadPose.query.filter(BadPose.interview_uuid == interview_uuid).all()
    be_records = BadExpression.query.filter(BadExpression.interview_uuid == interview_uuid).all()
    
    if not interview_record:
        return False
    
    be_list = [0,0,0,0]
    if(be_list):
        be_list = [x.num for x in sorted(be_records, \
            key=lambda record: emotion_type.index(record.expression))]
    bp_list = [0,0]
    if(bp_list):
        bp_list = [x.num for x in sorted(bp_records, \
            key=lambda record: pose_type.index(record.pose))]
    
    ret = InterviewResult(interview_uuid, int(turn_datetime_to_longint(interview_record.end_time)), \
        fake_ranking(interview_record.score), bp_list, be_list, interview_record.total_duration)
    
    print(interview_record.end_time)
    print(int(turn_datetime_to_longint(interview_record.end_time)))
    
    anss_records = AnsScore.query.filter(AnsScore.interview_uuid == interview_uuid).\
        order_by(AnsScore.index.asc()).all()
    
    que_list = [x.question for x in anss_records]
    ans_list = [x.answer for x in anss_records]
    feedback_list = [x.feedback for x in anss_records]
    duration_list = [x.duration for x in anss_records]
    warning_list = [x.duration_warning for x in anss_records]
    warning_sentence = ["적절한 빠르기 입니다" if x == 0 else "말의 빠르기가 너무 느리다면 면접에서 불쾌감을 줄 수 있습니다." \
        for x in warning_list]
    
    feedback_item_list = []
    for i in range(len(que_list)):
        feedback_item_list.append(FeedbackItem(que_list[i], ans_list[i], feedback_list[i], \
            duration_list[i], warning_sentence[i]).__dict__)
    
    ret.feedbackList = feedback_item_list
    return jsonify(ret.__dict__)

@api.route('/make_interview_result/')
class send_interviewdate(Resource):
    def get(self):
        interview_uuid = request.args.get('interview_uuid')
        return return_interview_result(interview_uuid).json
    def post(self):
        print("make_interview_result")
        interview_uuid = request.get_json()['questionnaireUUID']
        badExpressions = request.get_json()['badExpressions']
        badPose = request.get_json()['badPose']
        progress = request.get_json()['progress']
        answers = request.get_json()['answers'] # [{answerUUID, questionUUID, answer, question}]
        durations = request.get_json()['durations']
        
        record = MockInterview.query.get(interview_uuid)
        if not record:
            print("not such interview", interview_uuid)
            return False
        record.total_duration = sum(durations)
        
        be_records = BadExpression.query.filter(BadExpression.interview_uuid == interview_uuid).all()
        if(be_records):
            for be_record in be_records:
                db.session.delete(be_record)
        bp_records = BadPose.query.filter(BadPose.interview_uuid == interview_uuid).all()
        if(bp_records):
            for bp_record in bp_records:
                db.session.delete(bp_record)
        ans_records = AnsScore.query.filter(AnsScore.interview_uuid == interview_uuid).all()
        if(ans_records):
            for ans_record in ans_records:
                db.session.delete(ans_record)
        
        for i in range(len(badExpressions)):
            be_record = BadExpression(uuid.uuid1(), interview_uuid, emotion_type[i], badExpressions[i])
            db.session.add(be_record)
        
        for i in range(len(badPose)):
            bp_record = BadPose(uuid.uuid1(), interview_uuid, pose_type[i], badPose[i])
            db.session.add(bp_record)
        
        ques_list = [x['question'] for x in answers]
        ans_list = [x['answer'] for x in answers]
        ans_uuid_list = [x['answerUUID'] for x in answers]
        print(ques_list)
        print(ans_list)
        score_list, feedback_list, max_score, good_score = ScoreAns(ques_list, ans_list).score_answer()
        print(score_list)
        print(good_score)
        
        for i in range(len(answers)):
            warning = False
            if(durations[i] != 0 and \
                int(len(ans_list[i])/durations[i]) <  fake_duration_standard):
                warning = True
            ans_record = AnsScore(ans_uuid_list[i], interview_uuid, ques_list[i], ans_list[i], \
                feedback_list[i], score_list[i], durations[i], i+1, warning)
            db.session.add(ans_record)
        
        db.session.commit()
        
        FeedbackItem_list = []
        for i in range(len(durations)):
            warning_sentence = "적절한 빠르기 입니다"
            if(durations[i] != 0 and \
                int(len(ans_list[i])/durations[i]) <  fake_duration_standard):
                warning_sentence = "말의 빠르기가 너무 느리다면 면접에서 불쾌감을 줄 수 있습니다."
            FeedbackItem_list.append(FeedbackItem(ques_list[i], ans_list[i], feedback_list[i], \
                durations[i], warning_sentence).__dict__)
        
        fake_score = sum(score_list)
        fake_rank = fake_ranking(fake_score, max_score, good_score)
        total_duration = progress
        
        try:
            interview_record = MockInterview.query.get(interview_uuid)
            interview_record.score = fake_score
            script_record = SynthesisSelfIntroduction.query.get(interview_record.referenced_script)
            script_record.interview = 1
        except:
            return False
        db.session.commit()
        
        print(int(today_return()))
        return jsonify(InterviewResult(interview_uuid, int(today_return())*1000, fake_rank, badPose, \
            badExpressions, total_duration, FeedbackItem_list).__dict__)

@api.route('/memo/')
class interview_memo(Resource):
    def get(self):
        interview_uuid = request.args.get('interview_uuid')
        user_uuid = request.args.get('user_uuid')
        
        interview_record = MockInterview.query.get(interview_uuid)
        if(not interview_record or interview_record.interview_host_uuid != user_uuid):
            return False
        
        return jsonify(interview_record.self_memo)
    def post(self):
        input_json = request.get_json()
        interview_uuid = request.args.get('interview_uuid')
        user_uuid = request.args.get('user_uuid')
        memo = input_json['memo']
        
        interview_record = MockInterview.query.get(interview_uuid)
        if(not interview_record or interview_record.interview_host_uuid != user_uuid):
            return False
        
        try:
            interview_record.self_memo = memo
            db.session.commit()
        except:
            return False
        
        return True

@api.route('/interview_list/')
class interview_list(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        interview_records = MockInterview.query.\
            filter(MockInterview.interview_host_uuid == user_uuid, MockInterview.score > -1).\
                order_by(MockInterview.end_time.desc()).all()
        
        if(not interview_records):
            return []
        
        interview_uuid_list = [x.interview_uuid for x in interview_records]
        ret = []
        
        print(interview_uuid_list)
        
        for interview_uuid in interview_uuid_list:
            ret.append(return_interview_result(interview_uuid).json)
            
        print(ret)
        return ret
        
@api.route('/user_score_list/')
class user_score(Resource):
    def get(self):
        user_uuid = request.args.get('user_uuid')
        interview_records = MockInterview.query.\
            filter(MockInterview.interview_host_uuid == user_uuid, MockInterview.score > -1).\
                order_by(MockInterview.end_time.asc()).all()
        
        if(not interview_records):
            return []
        
        scores = [{"date" :  int(turn_datetime_to_longint(x.end_time)), "score" : x.score} \
            for x in interview_records]
        scores_c = [{"date" :  int(turn_datetime_to_longint(x.end_time)), "score" : fake_ranking(x.score)} \
            for x in interview_records]
        print("score")
        print(scores_c)
        
        min_score = min(scores, key=lambda x:x["score"])["score"]
        print(min_score)
        max_score = max(scores, key=lambda x:x["score"])["score"]
        print(max_score)
        recent_date = scores[-1]["date"]
        
        
        return jsonify({"max_score": fake_ranking(max_score), "min_score": fake_ranking(min_score), \
            "scores": scores_c, "recently_date": recent_date})
        
        
            
        
                
        
        
        
        
        
        
        

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from database import module

class UserAdminView(ModelView):
    form_columns = ['user_uuid', 'git_nickname', 'interesting_field', 'name', 'email', 'att_continue']
    column_display_pk = True
    
class SynthesisSelfIntroductionAdminView(ModelView):
    form_columns = ['script_uuid', 'script_host', 'script_date', 'script_title', 'question']
    column_display_pk = True
    
class CommonQueAdminView(ModelView):
    form_columns = ['ques_uuid', 'question', 'ques_type', 'recommandation']
    column_display_pk = True
    
class IndividualQueAdminView(ModelView):
    form_columns = ['ques_uuid', 'user_uuid', 'script_uuid']
    '''
    column_list = ['ques_uuid', 'user_uuid', 'script_uuid']
    form_args = {
        'user_uuid': {
            'query_factory': lambda: module.User.query.all(),
            'get_pk': lambda a: a.user_uuid,
            'label': 'User'
        }
    }
    '''
    column_display_pk = True
    
class AttendanceAdminView(ModelView):
    form_columns = ['att_uuid', 'user_uuid', 'att_date']
    column_display_pk = True
    
class MockInterviewAdminView(ModelView):
    form_columns = ['interview_uuid',
                    'interview_host_uuid',
                    'referenced_script',
                    'individual_question1',
                    'individual_question2',
                    'common_question1',
                    'common_question2',
                    'common_question3',
                    'end_time',
                    'self_memo']
    column_display_pk = True

class SelfIntroductionAAdminView(ModelView):
    form_columns = ['script_ans_uuid', 'user_uuid', 'script_ques_uuid', 'answer']
    column_display_pk = True
    
class SelfIntroductionQAdminView(ModelView):
    form_columns = ['script_ques_uuid', 'question', 'index', 'tip']
    column_display_pk = True
    
class TodayQueAdminView(ModelView):
    form_columns = ['tq_uuid', 'user_uuid', 'today_ques', 'user_memo', 'date']
    column_display_pk = True
    
class CommentRecommandationAdminView(ModelView):
    form_columns = ['cr_uuid', 'user_uuid']
    column_display_pk = True
    
class CommunityCommentAdminView(ModelView):
    form_columns = ['cc_uuid', 'user_uuid', 'common_ques', 'comment', 'date', 'recommandation']
    column_display_pk = True
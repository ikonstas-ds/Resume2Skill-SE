indexes = {
    'BUSINESS_TYPE': [('business_type',)],
    'CLASSIFICATION': [('classification',)],
    'DUTIES': [('duties', 'duties_lg')],
    'EDUCATION': [
        ('frm_id', 'cnd_id', 'app_id', 'education_type', 'education_category'),
        ('frm_id', 'cnd_id', 'app_id')
    ],
    'EDUCATION_CATEGORY': [('education_category',)],
    'EDUCATION_SUBJECT': [('subject',)],
    'EDUCATION_TYPE': [('education_type',)],
    'EMPLOYER_DETAILS': [('employer_details',)],
    'EXPERIENCE': [('frm_id', 'cnd_id', 'app_id')],
    'EXPERIENCE_TYPE': [('experience_type',)],
    'MANAGERIAL_POSITION': [('managerial_position',)],
    'ORGANISATION_NAME': [('organisation_name',)],
    'PROFILE': [('frm_id', 'cnd_id', 'app_id'), ('frm_id',)],
    'TEST_STATUS': [('frm_id', 'cnd_id', 'app_id', 'status')],
    'COMPETITION': [('comp_id',)],
    'FOLLOW_UP_ANSWER': [('frm_id',)],
    'FOLLOW_UP_ANSWER_TEXT': [('follow_up_answer_text',)],
    'SKILL': [
        ('skill_id', 'conceptUri', 'reuseLevel', 'skillType', 'preferred_label', 'description'),
        ('skill_id',),
        ('conceptUri',)],
    'OCCUPATION': [
        ('occupation_id', 'conceptUri', 'iscoGroup', 'preferredLabel', 'description'),
        ('occupation_id',),
        ('conceptURI',)
    ]
}

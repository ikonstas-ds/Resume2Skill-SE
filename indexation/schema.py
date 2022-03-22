indexes = {
    'EXPERIENCE': [('ID', 'experience_type')],
    'EXPERIENCE_TYPE': [('experience_type',)],
    # 'EXPERIENCE_DESCRIPTION': [('experience_description',)],
    'PROFILE': [('ID',)],
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

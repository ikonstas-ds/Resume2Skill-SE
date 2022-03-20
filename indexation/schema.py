indexes = {
    'EXPERIENCE': [('ID', 'experience_description', 'experience_type')],
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

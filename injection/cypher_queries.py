"""
injections use a FOREACH clause with an IN CASE WHEN condition as DUTIES might be null, and creating nodes with null
values is neither sensible nor even allowed.
See https://neo4j.com/developer/kb/conditional-cypher-execution/#_using_foreach_for_write_only_cypher for reference.
"""

injections = {
    'experiences': """
        UNWIND $experiences as exp
        MERGE (prof:PROFILE {frm_id:exp.FRM_ID, cnd_id:exp.CND_ID, app_id:exp.APP_ID})
    
        MERGE (experience:EXPERIENCE {
            frm_id:exp.FRM_ID, 
            cnd_id:exp.CND_ID, 
            app_id:exp.APP_ID, 
            experience_type:exp.EXPERIENCE_TYPE, 
            employer_details:exp.EMPLOYER_DETAILS, 
            managerial_position:exp.MANAGERIAL_POSITION
            })
        MERGE (prof)-[:HAS_EXPERIENCE]->(experience)
        
        MERGE (managerial_position:MANAGERIAL_POSITION {managerial_position:exp.MANAGERIAL_POSITION}) 
        MERGE (experience)-[:IS_MANAGERIAL_POSITION]->(managerial_position)
        
        MERGE (experience_type:EXPERIENCE_TYPE {experience_type:exp.EXPERIENCE_TYPE}) 
        MERGE (experience)-[:IS_OF_TYPE]->(experience_type)
        
        FOREACH (
            _ IN CASE WHEN exp.CLASSIFICATION IS NOT NULL THEN [1] ELSE [] END |
            SET experience.classification = exp.CLASSIFICATION
            MERGE (classification:CLASSIFICATION {classification:exp.CLASSIFICATION}) 
            MERGE (experience)-[:HAS_CLASSIFICATION]->(classification)
        )
        
        MERGE (employer_details:EMPLOYER_DETAILS {employer_details:exp.EMPLOYER_DETAILS}) 
        MERGE (experience)-[:IS_AT_EMPLOYER]->(employer_details) 
        
        FOREACH (
            _ IN CASE WHEN exp.BUSINESS_TYPE_EXTRA_INFO IS NOT NULL THEN [1] ELSE [] END |
            SET experience.business_type = exp.BUSINESS_TYPE_EXTRA_INFO 
            MERGE (business_type:BUSINESS_TYPE {business_type:exp.BUSINESS_TYPE_EXTRA_INFO}) 
            MERGE (employer_details)-[:IS_OF_BUSINESS_TYPE]->(business_type)
        )
        
        FOREACH (
            _ IN CASE WHEN exp.DUTIES IS NOT NULL THEN [1] ELSE [] END |
            SET experience.duties = exp.DUTIES
            MERGE (duties:DUTIES {duties:exp.DUTIES, duties_lg:exp.DUTIES_LG}) 
            MERGE (experience)-[:HAS_DUTIES]->(duties)
        )
    """,
    'education': """
        UNWIND $education as edu
        MERGE (prof:PROFILE {frm_id:edu.FRM_ID, cnd_id:edu.CND_ID, app_id:edu.APP_ID})
    
        MERGE (education:EDUCATION {
            frm_id:edu.FRM_ID, 
            cnd_id:edu.CND_ID, 
            app_id:edu.APP_ID, 
            education_type:toLower(edu.EDUCATION_TYPE), 
            education_category:toLower(edu.EDUCATION_CATEGORY) 
            })
        MERGE (prof)-[:HAS_EDUCATION]->(education)
        
        MERGE (education_type:EDUCATION_TYPE {education_type:toLower(edu.EDUCATION_TYPE)})
        MERGE (education)-[:IS_OF_TYPE]->(education_type)
        
        MERGE (education_category:EDUCATION_CATEGORY {education_category:toLower(edu.EDUCATION_CATEGORY)})
        MERGE (education)-[:IS_OF_EDUCATION_CATEGORY]->(education_category)
        
        FOREACH (
            _ IN CASE WHEN edu.ORGANISATION_NAME IS NOT NULL THEN [1] ELSE [] END |
            MERGE (organisation_name:ORGANISATION_NAME {organisation_name:toLower(edu.ORGANISATION_NAME)})
            MERGE (education)-[:IS_AT_ORGANISATION]->(organisation_name)
        )
        
        FOREACH (
            _ IN CASE WHEN edu.SUBJECT IS NOT NULL THEN [1] ELSE [] END |
            SET education.subject = edu.SUBJECT
            MERGE (subject:EDUCATION_SUBJECT {subject:toLower(edu.SUBJECT)})
            MERGE (education)-[:HAS_SUBJECT]->(subject)
        )
        
        MERGE (status:TEST_STATUS {frm_id:edu.FRM_ID, cnd_id:edu.CND_ID, app_id:edu.APP_ID, status:edu.STATUS})
        MERGE (prof)-[:HAS_TEST_STATUS]->(status)

        MERGE (compet:COMPETITION {comp_id:edu.TAL_COMPET_ID})
        MERGE (prof)-[:APPLIED_TO]->(compet)

        
    """,
    'follow_up_answers': """
        UNWIND $follow_up_answers as fup
        MERGE (prof:PROFILE {frm_id:fup.FRM_ID, cnd_id:fup.CND_ID, app_id:fup.APP_ID})
    
        MERGE (follow_up_answer:FOLLOW_UP_ANSWER {
            frm_id:fup.FRM_ID
            })
        MERGE (prof)-[:HAS_FOLLOW_UP_ANSWER]->(follow_up_answer)
        
        FOREACH (
            _ IN CASE WHEN fup.FOLLOW_UP_ANSWER IS NOT NULL THEN [1] ELSE [] END |
            MERGE (follow_up_answer_text:FOLLOW_UP_ANSWER_TEXT {follow_up_answer_text:fup.FOLLOW_UP_ANSWER}) 
            MERGE (follow_up_answer)-[:HAS_FOLLOW_UP_ANSWER_TEXT]->(follow_up_answer_text)
        )
    """  # SET follow_up_answer.follow_up_answer_text = fup.FOLLOW_UP_ANSWER_TEXT
}

esco_injection = {
    'esco_skills': """
        UNWIND $esco_skills as esco
        MERGE (skill:SKILL {
            skill_id:esco.skill_id,
            conceptUri:esco.conceptUri,
            reuseLevel:esco.reuseLevel,
            skillType:esco.skillType,
            preferredLabel:esco.preferredLabel,
            description:esco.description
            })
    """,
    'esco_occupations': """
        UNWIND $esco_occupations as esco
        MERGE (occ:OCCUPATION {
            occupation_id:esco.occupation_id,
            conceptUri:esco.conceptUri,
            iscoGroup:esco.iscoGroup,
            preferredLabel:esco.preferredLabel,
            description:esco.description
            })
    """,
    'occupations_skills': """
        UNWIND $occupations_skills as rel
        MATCH (occ:OCCUPATION {conceptUri:rel.occupationURI}), (skill:SKILL {conceptUri:rel.skillURI})
        MERGE (occ)-[:HAS_RELATED_ESSENTIAL_SKILL]->(skill)
    """
}




skills_injection = {
    'skills': """
        UNWIND $skills as skl
        MATCH (profile:PROFILE {frm_id: skl.FRM_ID}), (skill:SKILL {skill_id: skl.SKILL_ID})
        MERGE (profile)-[r:HAS_SKILL]->(skill)
        SET r.weight = skl.WEIGHT
    """
}

# TODO Update with follow up answers
full_injection = """
    UNWIND $data as profile_data
    MERGE (prof:PROFILE {frm_id:profile_data.FRM_ID, cnd_id:profile_data.CND_ID, app_id:profile_data.APP_ID})
    
    WITH profile_data, prof

    UNWIND profile_data.experiences as exp
    
    MERGE (experience:EXPERIENCE {
            frm_id:exp.FRM_ID, 
            cnd_id:exp.CND_ID, 
            app_id:exp.APP_ID, 
            experience_type:exp.EXPERIENCE_TYPE, 
            employer_details:exp.EMPLOYER_DETAILS, 
            managerial_position:exp.MANAGERIAL_POSITION
            })
    MERGE (prof)-[:HAS_EXPERIENCE]->(experience)
    
    MERGE (managerial_position:MANAGERIAL_POSITION {managerial_position:exp.MANAGERIAL_POSITION}) 
    MERGE (experience)-[:IS_MANAGERIAL_POSITION]->(managerial_position)
    
    MERGE (experience_type:EXPERIENCE_TYPE {experience_type:exp.EXPERIENCE_TYPE}) 
    MERGE (experience)-[:IS_OF_TYPE]->(experience_type)
    
    FOREACH (
        _ IN CASE WHEN exp.CLASSIFICATION IS NOT NULL THEN [1] ELSE [] END |
        SET experience.classification = exp.CLASSIFICATION
        MERGE (classification:CLASSIFICATION {classification:exp.CLASSIFICATION}) 
        MERGE (experience)-[:HAS_CLASSIFICATION]->(classification)
    )
    
    MERGE (employer_details:EMPLOYER_DETAILS {employer_details:exp.EMPLOYER_DETAILS}) 
    MERGE (experience)-[:IS_AT_EMPLOYER]->(employer_details) 
    
    FOREACH (
        _ IN CASE WHEN exp.BUSINESS_TYPE_EXTRA_INFO IS NOT NULL THEN [1] ELSE [] END |
        SET experience.business_type = exp.BUSINESS_TYPE_EXTRA_INFO 
        MERGE (business_type:BUSINESS_TYPE {business_type:exp.BUSINESS_TYPE_EXTRA_INFO}) 
        MERGE (employer_details)-[:IS_OF_BUSINESS_TYPE]->(business_type)
    )
    
    FOREACH (
        _ IN CASE WHEN exp.DUTIES IS NOT NULL THEN [1] ELSE [] END |
        SET experience.duties = exp.DUTIES
        MERGE (duties:DUTIES {duties:exp.DUTIES}) 
        MERGE (experience)-[:HAS_DUTIES]->(duties)
    )

    WITH profile_data, prof

    UNWIND profile_data.education as edu

    MERGE (education:EDUCATION {
            frm_id:edu.FRM_ID, 
            cnd_id:edu.CND_ID, 
            app_id:edu.APP_ID, 
            education_type:toLower(edu.EDUCATION_TYPE), 
            education_category:toLower(edu.EDUCATION_CATEGORY) 
            })
    MERGE (prof)-[:HAS_EDUCATION]->(education)
    
    FOREACH (
        _ IN CASE WHEN edu.QUALIFICATION_TYPE IS NOT NULL THEN [1] ELSE [] END |
        set education.qualification_type = edu.QUALIFICATION_TYPE
        MERGE (qualification_type:QUALIFICATION_TYPE {qualification_type:toLower(edu.QUALIFICATION_TYPE)})
        MERGE (education)-[:IS_OF_QUALIFICATION_TYPE]->(qualification_type)
    )
    
    MERGE (education_type:EDUCATION_TYPE {education_type:toLower(edu.EDUCATION_TYPE)})
    MERGE (education)-[:IS_OF_TYPE]->(education_type)
    
    MERGE (education_category:EDUCATION_CATEGORY {education_category:toLower(edu.EDUCATION_CATEGORY)})
    MERGE (education)-[:IS_OF_EDUCATION_CATEGORY]->(education_category)
    
    FOREACH (
        _ IN CASE WHEN edu.ORGANISATION_NAME IS NOT NULL THEN [1] ELSE [] END |
        MERGE (organisation_name:ORGANISATION_NAME {organisation_name:toLower(edu.ORGANISATION_NAME)})
        MERGE (education)-[:IS_AT_ORGANISATION]->(organisation_name)
    )
    
    FOREACH (
        _ IN CASE WHEN edu.SUBJECT IS NOT NULL THEN [1] ELSE [] END |
        SET education.subject = edu.SUBJECT
        MERGE (subject:EDUCATION_SUBJECT {subject:toLower(edu.SUBJECT)})
        MERGE (education)-[:HAS_SUBJECT]->(subject)
    )
    
    MERGE (status:TEST_STATUS {frm_id:edu.FRM_ID, cnd_id:edu.CND_ID, app_id:edu.APP_ID, status:edu.STATUS})
    MERGE (prof)-[:HAS_TEST_STATUS]->(status)
"""

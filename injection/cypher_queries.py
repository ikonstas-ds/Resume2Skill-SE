"""
injections use a FOREACH clause with an IN CASE WHEN condition as DUTIES might be null, and creating nodes with null
values is neither sensible nor even allowed.
See https://neo4j.com/developer/kb/conditional-cypher-execution/#_using_foreach_for_write_only_cypher for reference.
"""

injections = {
    'experiences': """
        UNWIND $experiences as exp
        MERGE (prof:PROFILE {ID:exp.ID})
    
        MERGE (experience:EXPERIENCE {
            ID:exp.ID,
            exp_id: exp.ind, 
            experience_description:exp.experience_description,
            experience_type:exp.Category
            })
        MERGE (prof)-[:HAS_EXPERIENCE]->(experience)

        MERGE (experience_description:EXPERIENCE_DESCRIPTION {experience_description:exp.experience_description, exp_id: exp.ind})
        MERGE (experience)-[:HAS_DESCRIPTION]->(experience_description)

        MERGE (experience_type:EXPERIENCE_TYPE {experience_type:exp.Category})
        MERGE (experience)-[:IS_OF_TYPE]->(experience_type)
    """
}
"""
FOREACH (
            _ IN CASE WHEN exp.experience_type IS NOT NULL THEN [1] ELSE [] END |
            SET experience.experience_type = exp.Category
            MERGE (experience_type:EXPERIENCE_TYPE {experience_type:exp.Category})
            MERGE (experience)-[:IS_OF_TYPE]->(experience_type)
        )
"""


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
        MATCH (profile:PROFILE {ID: skl.ID}), (skill:SKILL {skill_id: skl.SKILL_ID})
        MERGE (profile)-[r:HAS_SKILL]->(skill)
        SET r.weight = skl.WEIGHT
    """
}
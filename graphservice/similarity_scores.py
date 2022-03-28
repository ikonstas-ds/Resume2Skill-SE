sim_score_formulas = {
'query_f1':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WITH collect(distinct s) as skills, n, size(collect(s)) as countSourceSkills
UNWIND skills as skill
MATCH (m:PROFILE)-[r2:HAS_SKILL]->(skill)
MATCH (m)-[:HAS_EXPERIENCE]-(exp)
MATCH (q {ID:$sourceId})-[r3:HAS_SKILL]->(skill)
WITH q, m, sum(r3.weight) + sum(r2.weight) as simScore, countSourceSkills, count(r2) as countTargetSkills, 
    collect(DISTINCT skill.preferredLabel) as skillLabels, collect(DISTINCT exp.experience_type) as experience_type
RETURN q as source, m as target, simScore, countSourceSkills, countTargetSkills, skillLabels,
        experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
""",

'query_f2':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WITH collect(distinct s) as skills, n, size(collect(s)) as countSourceSkills
UNWIND skills as skill
MATCH (m:PROFILE)-[r2:HAS_SKILL]->(skill)
MATCH (m)-[:HAS_EXPERIENCE]-(exp)
MATCH (q {ID:$sourceId})-[r3:HAS_SKILL]->(skill)
WITH q, m, sum(r3.weight*r2.weight) as simScore, countSourceSkills, count(r2) as countTargetSkills, 
    collect(DISTINCT skill.preferredLabel) as skillLabels, collect(DISTINCT exp.experience_type) as experience_type
RETURN q as source, m as target, simScore, countSourceSkills, countTargetSkills, skillLabels,
        experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
""",

'query_f3':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WITH collect(distinct s) as skills, n, size(collect(s)) as countSourceSkills
UNWIND skills as skill
MATCH (m:PROFILE)-[r2:HAS_SKILL]->(skill)
MATCH (m)-[:HAS_EXPERIENCE]-(exp)
MATCH (q {ID:$sourceId})-[r3:HAS_SKILL]->(skill)
WITH q, m, count(DISTINCT skill) as simScore, countSourceSkills, count(r2) as countTargetSkills,
    collect(DISTINCT skill.preferredLabel) as skillLabels, count(DISTINCT skill) as countCommonSkills,
    collect(DISTINCT exp.experience_type) as experience_type
RETURN q as source, m as target, simScore, countCommonSkills,
    countSourceSkills, countTargetSkills, skillLabels, experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countCommonSkills,
        countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
""",

'query_f4':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WITH collect(distinct s) as skills, n, size(collect(DISTINCT s)) as countSourceSkills,
    collect(DISTINCT s.skill_id) as skillIds
UNWIND skills as skill
MATCH (m:PROFILE)-[:HAS_SKILL]->(skill)
WITH COLLECT(DISTINCT m) as profiles, n, countSourceSkills, skillIds, skill
UNWIND profiles as prof
MATCH (prof)-[r2:HAS_SKILL]->(skillAll)
MATCH (prof)-[:HAS_EXPERIENCE]-(exp)
WITH n, prof, size(apoc.coll.intersection(skillIds,collect(DISTINCT skillAll.skill_id))) as countCommonSkills, countSourceSkills, count(DISTINCT skillAll) as countTargetSkills, count(DISTINCT r2) as countOverlap, collect(DISTINCT skill.preferredLabel) as skillLabels, collect(DISTINCT exp.experience_type) as experience_type, skillIds
WITH n, prof, round((countCommonSkills*countCommonSkills*1.0/(countSourceSkills*countTargetSkills)), 5) as simScore, countCommonSkills, countSourceSkills, countTargetSkills, skillLabels, experience_type
RETURN n as source, prof as target, simScore, countCommonSkills,
        countSourceSkills, countTargetSkills, skillLabels,
        experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countCommonSkills, countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
""",

'query_f1_no_cross_sector':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WHERE s.reuseLevel<>'cross-sector'
WITH collect(distinct s) as skills, n, size(collect(s)) as countSourceSkills
UNWIND skills as skill
MATCH (m:PROFILE)-[r2:HAS_SKILL]->(skill)
MATCH (m)-[:HAS_EXPERIENCE]-(exp)
MATCH (q {ID:$sourceId})-[r3:HAS_SKILL]->(skill)
WHERE skill.reuseLevel<>'cross-sector'
WITH q, m, sum(r3.weight) + sum(r2.weight) as simScore, countSourceSkills, count(r2) as countTargetSkills, 
    collect(DISTINCT skill.preferredLabel) as skillLabels, collect(DISTINCT exp.experience_type) as experience_type
RETURN q as source, m as target, simScore, countSourceSkills, countTargetSkills, skillLabels,
        experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
""",


'query_f2_no_cross_sector':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WHERE s.reuseLevel<>'cross-sector'
WITH collect(distinct s) as skills, n, size(collect(s)) as countSourceSkills
UNWIND skills as skill
MATCH (m:PROFILE)-[r2:HAS_SKILL]->(skill)
MATCH (m)-[:HAS_EXPERIENCE]-(exp)
MATCH (q {ID:$sourceId})-[r3:HAS_SKILL]->(skill)
WHERE skill.reuseLevel<>'cross-sector'
WITH q, m, sum(r3.weight*r2.weight) as simScore, countSourceSkills, count(r2) as countTargetSkills, 
    collect(DISTINCT skill.preferredLabel) as skillLabels, collect(DISTINCT exp.experience_type) as experience_type
RETURN q as source, m as target, simScore, countSourceSkills, countTargetSkills, skillLabels,
        experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
""",


'query_f3_no_cross_sector':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WHERE s.reuseLevel<>'cross-sector'
WITH collect(distinct s) as skills, n, size(collect(s)) as countSourceSkills
UNWIND skills as skill
MATCH (m:PROFILE)-[r2:HAS_SKILL]->(skill)
MATCH (m)-[:HAS_EXPERIENCE]-(exp)
MATCH (q {ID:$sourceId})-[r3:HAS_SKILL]->(skill)
WHERE skill.reuseLevel<>'cross-sector'
WITH q, m, count(DISTINCT skill) as simScore, countSourceSkills, count(r2) as countTargetSkills,
    collect(DISTINCT skill.preferredLabel) as skillLabels, count(DISTINCT skill) as countCommonSkills,
    collect(DISTINCT exp.experience_type) as experience_type
RETURN q as source, m as target, simScore, countCommonSkills,
    countSourceSkills, countTargetSkills, skillLabels, experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countCommonSkills,
        countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
""",


'query_f4_no_cross_sector':"""
MATCH (n:PROFILE {ID:$sourceId})-[r1:HAS_SKILL]->(s:SKILL)
WHERE s.reuseLevel<>'cross-sector'
WITH collect(distinct s) as skills, n, size(collect(DISTINCT s)) as countSourceSkills,
    collect(DISTINCT s.skill_id) as skillIds
UNWIND skills as skill
MATCH (m:PROFILE)-[:HAS_SKILL]->(skill)
WITH COLLECT(DISTINCT m) as profiles, n, countSourceSkills, skillIds, skill
UNWIND profiles as prof
MATCH (prof)-[r2:HAS_SKILL]->(skillAll)
MATCH (prof)-[:HAS_EXPERIENCE]-(exp)
WHERE skill.reuseLevel<>'cross-sector'
WITH n, prof, size(apoc.coll.intersection(skillIds,collect(DISTINCT skillAll.skill_id))) as countCommonSkills, countSourceSkills, count(DISTINCT skillAll) as countTargetSkills, count(DISTINCT r2) as countOverlap, collect(DISTINCT skill.preferredLabel) as skillLabels, collect(DISTINCT exp.experience_type) as experience_type, skillIds
WITH n, prof, round((countCommonSkills*countCommonSkills*1.0/(countSourceSkills*countTargetSkills)), 5) as simScore, countCommonSkills, countSourceSkills, countTargetSkills, skillLabels, experience_type
RETURN n as source, prof as target, simScore, countCommonSkills,
        countSourceSkills, countTargetSkills, skillLabels,
        experience_type
ORDER BY simScore DESCENDING, source, target, simScore, countCommonSkills, countSourceSkills, countTargetSkills, skillLabels, experience_type
LIMIT $limit
"""
}

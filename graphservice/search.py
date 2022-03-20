from graphservice.neoservice import neoconnection
from graphservice.similarity_scores import sim_score_formulas


def insert_question(question_text):
    tx = neoconnection.graph.begin()

    statement = """
                        MERGE (b:BotQuestion {text:toLower($text)}) 
                        return id(b) as id

                        """
    params = {'text': question_text}
    new_node = tx.run(statement, params)
    question_id = new_node.data()[-1]['id']
    tx.commit()

    return int(question_id)


def encode_feedback(profile_id, search_id, feedback):
    tx = neoconnection.graph.begin()
    statement = """
                Match (profile:PROFILE)
                Match (search:BotQuestion)
                where id(search)=$search_id and profile.frm_id=$profile_id
                merge (profile)-[r:ANSWERS { feedback: $feedback }]->(search)
                """

    params = {"profile_id": int(profile_id), "search_id": int(search_id), "feedback": feedback}
    new_node = tx.run(statement, params)

    tx.commit()
    return 'SUCCESS'


# def search_similar_profiles(**kwargs):
#     """
#     Search similar profiles
#     :param kwargs: sourceIds: The ids of items from which we need to compute similarities. Defaults to all the items provided in the data parameter.
#     ,targetIds:The ids of items to which we need to compute similarities. Defaults to all the items provided in the data parameter,
#     limit: Limit of returned profiles

#     :return: array of profiles
#     """
#     statement = """

#                                 match (n:PROFILE)-[*1..2]-(matcr)
#                                 where not(labels(matcr)  in [['PROFILE']])

#                                 WITH {item:id(n) ,frm_id:n.frm_id, categories: collect(id(matcr))} AS userData
#                                 WITH collect(userData) AS data

#                                 with data, [value in data WHERE value.frm_id IN $sourceIds | value.item ] AS sourceIds , [value in data WHERE not (value.frm_id  IN $sourceIds)  | value.item ] AS targetIds 
#                                 CALL gds.alpha.similarity.overlap.stream({data: data, sourceIds:sourceIds,  topK: 3})
                                
#                                 YIELD item1, item2, count1, count2, intersection, similarity
                                
#                                 with gds.util.asNode(item2) AS profile,similarity ,intersection
#                                 with collect(distinct profile) as profiles
#                                     unwind profiles[..$limit] as profile
#                                     match (profile)-[r2]-(experience:EXPERIENCE)
#                                     match (profile)-[r3]-(education:EDUCATION)
#                                     WITH {profile:profile , experience: collect(distinct (experience)), education: collect(distinct (education))} AS userData      
#                                     RETURN userData                    

#                 """

#     targetIds = kwargs.pop('targetIds', [])

#     params = {'sourceIds': kwargs.pop('sourceIds', []), 'targetIds': targetIds, 'limit': kwargs.pop('limit', 5)}
#     tx = neoconnection.graph.begin()
#     new_node = tx.run(statement, params)

#     tx.commit()
#     res = new_node.data()

#     return [dict(n)['userData'] for n in res]


def search_similar_profiles(**kwargs):
    """
    Search similar profiles
    Input:
        kwargs: 
            profile_id: The ids of items from which we need to compute similarities. Defaults to all the items provided in the data parameter.,
            sim_score: The formula used for similarity score between profiles. Possible values are 'formula1', 'formula2', 
                'formula3'
            topk: The number of profiles to return
            no_cross_sector: True if no cross-sector skills are considered. Default values is False.
    Output:
    List of dictionaries in the form:
    [
    'profile':{'cnd_id':"<int>", 'app_id':"<int>", 'frm_id':"<int>"},
    'education':[{'subject':"<str>", 'education_category':"<str>", 'education_type':"<str>",
                'cnd_id':<int>", 'app_id':"<int>", 'frm_id':"<int>"}, ...],
    'experience':[{'experience_type':"<str>", 'employer_details':"<str>", classification:"<str>",
                'managerial_position':"<str>", 'duties':"<str>",
                'cnd_id':<int>", 'app_id':"<int>", 'frm_id':"<int>"}, ...],
    'simScore':"<float>", skillLabels:["<str>",...]
    ]
    """

    sim_score = kwargs.pop('sim_score', 'formula4')

    query_score = ""
    if sim_score=='formula1':
        query_score = 'query_f1'
    elif sim_score=='formula2':
        query_score = 'query_f2'
    elif sim_score=='formula3':
        query_score = 'query_f3'
    elif sim_score=='formula4':
        query_score = 'query_f4'
    else:
        raise Exception(f"There is no formula with the name {query_score}")
    

    no_cross_sector = kwargs.pop('no_cross_sector', None)
    if no_cross_sector:
        query_score += '_no_cross_sector'

    query = sim_score_formulas[query_score]

    statement = """
    call{
    """ + query + """
    }
    WITH target, simScore, skillLabels
    MATCH (target)-[r2]-(experience:EXPERIENCE)
    MATCH (target)-[r3]-(education:EDUCATION)
    WITH {profile:target , experience: collect(distinct (experience)),
            education: collect(distinct (education)), simScore:simScore, skillLabels: skillLabels} AS userData      
    RETURN userData
    """
    
    tx = neoconnection.graph.auto(readonly=True)
    
    limit = kwargs.pop('topk', 30)
    if not limit:
        limit = 30
    
    params = {'sourceId': kwargs.pop('sourceId', ""), 'limit': limit}
    
    new_node = tx.run(statement, params)
    # new_node.to_data_frame().head(3)

    res = new_node.data()
    return [dict(n)['userData'] for n in res]





def search_full_text(**kwargs):
    """

    :param kwargs: index: name of text index, term: search term, limit: number of profiles to return
    :return: search id,array of profiles,filters,centrality filters,outliers

    """
    statement = """                 
                                    
                                    CALL db.index.fulltext.queryNodes($index, $term) YIELD node as found_term, score
                                    match (profile:PROFILE)-[r1]-(found_term)
                                    with collect(distinct profile) as profiles
                                    unwind profiles[..$limit] as profile
                                    match (profile)-[r2]-(experience:EXPERIENCE)
                                    match (profile)-[r3]-(education:EDUCATION)
                                    WITH {profile:profile, experience: collect(distinct (experience)), education: collect(distinct (education))} AS userData 
                                    RETURN userData

                """

    params = {'index': kwargs.pop('index', ""), 'term': kwargs.pop('term', ''), 'limit': kwargs.pop('limit', 10)}
    search_id = insert_question(params['term'])
    tx = neoconnection.graph.begin()
    new_node = tx.run(statement, params)

    tx.commit()
    res = new_node.data()
    profiles = [dict(n)['userData'] for n in res]
    statement = """
                            
                            match (n:PROFILE)-[*1..1]-(matcr)
                            where not(labels(matcr) in [['PROFILE'],["BotQuestion"]])
                            and id(n) in $ids
                            with collect (distinct labels(matcr)) as labels,n
                            unwind labels as label
                            match (n2:PROFILE)-[*1..1]-(m)
                            where  size(apoc.coll.intersection(labels(m), label))>0
                            and id(n2) in $ids
                            WITH {label :label[0] , attributes: collect(distinct (m))} AS filters    
                            return filters

    """


    ids = [n['profile'].identity for n in profiles]

    params = {'ids': ids, 'nrhops': "2"}
    tx = neoconnection.graph.begin()
    new_node = tx.run(statement, params)

    tx.commit()
    res = new_node.data()
    filters = [dict(n)['filters'] for n in res]

    tx = neoconnection.graph.begin()

    statement = """ with gds.graph.exists('my-cypher-graph') as exists return exists ; """

    new_node = tx.run(statement, {})

    sub_gr = new_node.data()[0]
    tx.commit()
    if sub_gr['exists']:

        tx = neoconnection.graph.begin()
        statement = """ CALL gds.graph.drop('my-cypher-graph') YIELD graphName; """

        new_node = tx.run(statement, {})
        sub_gr = new_node.to_subgraph()
        tx.commit()

    tx = neoconnection.graph.begin()
    cetntrality_filters = []

    statement = """
    
         CALL gds.graph.create.cypher('my-cypher-graph',
         'MATCH (n)-[*1..2]-(r)  
         WHERE id(n) IN $base_ids and not(labels(r) in [["PROFILE"],["BotQuestion"]])
         RETURN id(n) AS id
            UNION
            MATCH (n)-[*1..2]-(r)  
         WHERE id(n) IN $base_ids and not(labels(r) in [["PROFILE"],["BotQuestion"]])
         RETURN id(r) AS id',
         'MATCH (n)-[*1..2]-(r)  where id(n) in  $base_ids and not(labels(r) in [["PROFILE"],["BotQuestion"]])
         RETURN id(n) AS source, id(r) AS target',
         {parameters:{base_ids:$base_ids}})
         YIELD graphName, nodeCount, relationshipCount, createMillis
         CALL gds.pageRank.stream('my-cypher-graph' , { maxIterations: 20,  dampingFactor: 0.85 })
         YIELD nodeId, score
         with gds.util.asNode(nodeId)  as res,score order by score DESC
         with collect(distinct { n:res, score:score })[..$topk] as res
         return res
         
     """
    params = {'base_ids': ids, 'topk': 10}

    try:

        new_node = tx.run(statement, params)
        res = new_node.data()
        cetntrality_filters = [dict(n) for n in res[0]['res']]

    except Exception as exc:
        print(exc)

    tx = neoconnection.graph.begin()
    stats = []
    statement = """

            CALL gds.pageRank.stats('my-cypher-graph' , { maxIterations: 20,  dampingFactor: 0.85 })
            YIELD centralityDistribution
            with  centralityDistribution.mean  as mean, (centralityDistribution.p75 - centralityDistribution.p25)*3 as interquartile_range ,centralityDistribution
            CALL gds.pageRank.stream('my-cypher-graph' , { maxIterations: 20,  dampingFactor: 0.85 })
            YIELD nodeId, score
            where score < abs(centralityDistribution.p25-(centralityDistribution.stdDev*1.5))
            with gds.util.asNode(nodeId)  as res,score,mean,interquartile_range,abs(score-mean) as dist,centralityDistribution
            with collect(distinct { n:res, score:score, interquartile_range:interquartile_range,p75:centralityDistribution.p75,p25:centralityDistribution.p25 }) as res
            return res

         """
    params = {'base_ids': ids}

    try:
        new_node = tx.run(statement, params)
        res = new_node.data()
        outliers = [dict(n) for n in res[0]['res']]
    except Exception as exc:
        print(exc)
    tx.commit()

    tx = neoconnection.graph.begin()
    params = {'ids': ids, "search_id": search_id, 'feedback': 'PROPOSED_SEARCH'}
    statement = """
                    Match (profile:PROFILE)
                    where id(profile) in $ids
                    Match (search:BotQuestion)
                    where id(search)=$search_id
                    merge (profile)-[r:PROPOSED { feedback: $feedback }]->(search)
        """
    new_node = tx.run(statement, params)
    tx.commit()

    return search_id, profiles, filters, cetntrality_filters, outliers


def query_profile_info(frm_ids):
    
    frm_ids = [int(item) for item in frm_ids]
    
    statement = """
    UNWIND $frm_ids as prof_id
    MATCH (profile:PROFILE {frm_id:prof_id})
    MATCH (profile)-[r2]-(experience:EXPERIENCE)
    MATCH (profile)-[r3]-(education:EDUCATION)
    WITH {profile:profile , experience: collect(distinct (experience)),
            education: collect(distinct (education)), skillLabels: collect(distinct (skill.preferredLabel))} AS userData      
    RETURN userData
    """
    
    tx = neoconnection.graph.auto(readonly=True)
        
    params = {'frm_ids': frm_ids}
    
    new_node = tx.run(statement, params)
    # new_node.to_data_frame().head(3)

    res = new_node.data()
    return [dict(n)['userData'] for n in res]


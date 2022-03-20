from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .bodies import *
import services.semantic_sim_aas.dlfunctions as semtc_sim_dlf
import services.overlap_sim_aas.dlfunctions as ovlp_sim_dlf
import services.keyword_extr_aas.dlfunctions as kwrd_ext_dlf
from graphservice import search
import numpy as np
from typing import Dict, List
# workaround - the original topics model was created with a packaged version of Top2Vec - pickle will raise
# a ModuleNotFoundError without this
from topic import Top2Vec
import topic
from sys import modules
modules['top2vecReworked'] = topic
topics_model = './topic/models/mcs50_ms25_cse0.12_csmleaf_main_overlap_3'
topic_searcher = Top2Vec.load(topics_model)
topic_searcher.embed = topic_searcher.get_transformer()

app = FastAPI(title='Intelligent Talent Search')


def numpy2py(a: np.ndarray):
    """
    A function to convert numpy arrays before json serialization.
    Covers issues with nan values.
    :param a: a numpy array
    :return: a list
    """
    if a.dtype.kind == 'f':
        nan_mask = np.isnan(a)
        a = a.astype(np.object)
        np.putmask(a, nan_mask, (None, ))
    return a.tolist()


@app.get("/",
         response_model=Dict[str, str],
         description='Get the status of the service.')
async def root() -> Body:
    return {"message": "The service is up and running."}


@app.get('/get-semantic-metrics',
         response_model=List[str],
         description='Get the list of available values for semantic similarity.')
def get_semantic_metrics() -> Body:
    return [d.value for _, d in enumerate(DistanceType)]


@app.post('/get-semantic-sims',
          response_model=List[float],
          description='Get the similarity between pairs of texts given a specified metric.')
async def get_semantic_similarities(semantic_query: SemanticQuery) -> Body:
    return semtc_sim_dlf.get_similarities(semantic_query.text_pairs, semantic_query.distance_type)


@app.post("/get-overlap-sims", response_model=str)
def get_overlap_similarities(overlap_query: OverlapQuery = Body(...)) -> Body:
    results = jsonable_encoder(ovlp_sim_dlf.get_similarities(overlap_query.term))
    return JSONResponse(content=results)


@app.post("/get-keywords", response_model=str)
def get_keywords(keywords_query: KeywordsQuery = Body(...)) -> Body:
    results = jsonable_encoder(
        kwrd_ext_dlf.extract_keywords(keywords_query.text),
        custom_encoder={np.ndarray: numpy2py})
    return JSONResponse(content=results)


@app.post("/get-tags", response_model=Tagging)
async def get_tags(tags_query: TagsQuery = Body(...)) -> Body:
    tags = []
    scores = []
    min_score = 0.0 if not tags_query.min_score else tags_query.min_score
    _, values, words = topic_searcher.get_document_n_topics(tags_query.texts, tags_query.num_tags, 1)
    for value_list, word_list in zip(values, words):
        tag_list = []
        score_list = []
        for value, words in zip(value_list, word_list):
            if value >= min_score:
                tag_list.append(words[0])
                score_list.append(value)
        tags.append(tag_list)
        scores.append(score_list)
    return {"tags": tags, "scores": scores}


get_sim_desc = """
Get most relevant profiles to a profile.
Input:
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
@app.post("/get-sim-profiles", response_model=str, description=get_sim_desc)
def get_overlap_similarities(profileQuery: ProfileQuery = Body(...)) -> Body:
    results = jsonable_encoder(search.search_similar_profiles(**{"sourceId":profileQuery.profile_id,
                "sim_score":profileQuery.score_formula, "no_cross_sector":profileQuery.no_cross_sector,
                "topk":profileQuery.topk}))
    return JSONResponse(content=results)


@app.post("/get-profile-info", response_model=str, description="Get profile information from a FRM_ID")
def get_profile_information(profileIDsQuery: ProfileIDsQuery = Body(...)) -> Body:
    results = jsonable_encoder(search.query_profile_info(profileIDsQuery.frm_ids))
    return JSONResponse(content=results)


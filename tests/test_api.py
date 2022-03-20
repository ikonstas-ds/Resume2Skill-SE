import requests
# import json

url = 'http://127.0.0.1:8000/'

# Test finding similar profiles to a profile
get_sim_profiles = 'get-sim-profiles'
profile_id = 5
score_formula = 'formula4'
no_cross_sector = False
topk = 30
data = {'profile_id':profile_id} #, 'score_formula':score_formula,
        # 'no_cross_sector':no_cross_sector, 'topk':topk}

res = requests.post(url+get_sim_profiles, json=data)
print(res.json())


# Test getting similarity score between two texts
# get_semantic_sims = 'get-semantic-sims'
# text1 = 'kobe bryant'
# text2 = 'michael jordan'

# data = {'text_pairs':[[text1,text2]], 'distance_type':'cosine'}
# res = requests.post(url+get_semantic_sims, json=data)
# print(res.json())


# Test getting relevant profiles to a query
# get_overlap_sims = 'get-overlap-sims'
# text = 'I am looking for a legal expert with experience in European Institutions and with knowledge of international law related to marine and environment'

# data = {'term':text}
# res = requests.post(url+get_overlap_sims, json=data)
# print(res.json())


# Test getting keywords of texts
# get_keywords = 'get-keywords'
# text = 'I am looking for a legal expert with experience in European Institutions and with knowledge of international law related to marine and environment'

# data = {'text':text}
# res = requests.post(url+get_keywords, json=data)
# print(res.json())


# Test getting topics from texts
# get_tags = 'get-tags'
# text = 'I am looking for a legal expert with experience in European Institutions and with knowledge of international law related to marine and environment'

# data = {'texts':[text]}
# res = requests.post(url+get_tags, json=data)
# print(res.json())


# Test getting profile information of given frm_ids
# get_profile_info = 'get-profile-info'
# frm_ids = [4,5]
# data = {'frm_ids': frm_ids}
# res = requests.post(url+get_profile_info, json=data)
# print(res.json())

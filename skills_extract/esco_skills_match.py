import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer, util
import os
try:
    import faiss
except:
    pass
from tqdm import tqdm
from collections import Counter
import time
import torch


def flatten(t):
    return [item for sublist in t for item in sublist]


class SkillExtractor():
    def __init__(self, esco_data_path='ESCO/skills_en.csv', model_name='all-mpnet-base-v2', dim=768, nlist=100):
        
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load sentence transformer model
        self.model = SentenceTransformer('sentence-transformers/' + model_name, device=device)

        # Load ESCO skills file
        self.esco_data = pd.read_csv(esco_data_path)
        self.skills_list = self.esco_data.description.values.tolist()

        #Create embedding index
        esco_embeddings_path = 'ESCO/esco_embedddings.npy'
        if not os.path.exists(esco_embeddings_path):
            self.embeddings_esco = self.model.encode(self.skills_list, convert_to_tensor=True)
            self.emb_index = {skill: self.embeddings_esco[i] for i, skill in enumerate(self.skills_list)}
            np.save(esco_embeddings_path, self.embeddings_esco)
        else:
            self.embeddings_esco = np.load('ESCO/esco_embedddings.npy')
        
        
        # Faiss initialisation for indexing embeddings
        self.dim = dim
        self.nlist = nlist
        quantizer = faiss.IndexFlatL2(dim)  # the other index
        self.index = faiss.IndexIVFFlat(quantizer, dim, nlist)
        assert not self.index.is_trained
        self.index.train(self.embeddings_esco)
        assert self.index.is_trained

        self.index.add(self.embeddings_esco)
    

    def load_profiles(self, data):

        if type(data) == str:
            with open(data, 'r', encoding='utf-8') as file:
                data: dict = json.load(file)
        
        df_exp = pd.DataFrame(data['experiences'])
        df_fup =  pd.DataFrame(data['follow_up_answers'])

        df_exp = df_exp[['FRM_ID', 'DUTIES']]
        df_fup = df_fup[['FRM_ID', 'FOLLOW_UP_ANSWER']]
        df_fup.rename(columns={'FOLLOW_UP_ANSWER': 'DUTIES'}, inplace=True)

        data = pd.concat([df_exp, df_fup])
        data.dropna(inplace=True)

        return data
    

    def skills_search(self, text, topk=5):
        emb_doc = self.model.encode([text])
        D, i = self.index.search(emb_doc, topk)     # actual search
        return i


    def multiple_skills_search(self, docs, topk=5):
        emb_doc = self.model.encode(docs)
        D, ids = self.index.search(emb_doc, topk)     # actual search
        return ids


    def get_skills_by_ids(self, ids):
        return self.esco_data.iloc[ids]
    

    def extract(self, data, topk=5, extract_path=None):
        duties_fup_embeddings = np.load('epso_data/duties_fup_embedddings.npy')

        if type(data) == str:
            with open(data, 'r', encoding='utf-8') as file:
                data: dict = json.load(file)

        
        D, ids = self.index.search(duties_fup_embeddings, topk)

        data['skills'] = pd.Series(data.index).apply(lambda i: ids[i])

        q = data.groupby('FRM_ID')
        prof_skills = []
        for frm_id, item in tqdm(q):
            counts = Counter(flatten(item.skills.tolist()))
            el = [{'FRM_ID': frm_id, 'SKILL_ID': int(item[0]), 'WEIGHT': item[1]} for item in list(counts.items())]
            prof_skills += el
        prof_skills_dict = dict()
        prof_skills_dict['skills'] = prof_skills

        if extract_path:
            with open(extract_path, 'w+') as f:
                json.dump(prof_skills_dict, f)
            return None

        return prof_skills_dict
    

    def calculate_embeddings(self, data):

        device = "cuda" if torch.cuda.is_available() else "cpu"

        print('Calculating embeddings for duties and follow up answers')
        a = time.time()
        duties_embeddings = self.model.encode(data['DUTIES'].tolist(), device=device, show_progress_bar=True)
        print(f'Calculation finished in {(time.time()-a)/3600} hours')


        np.save('epso_data/duties_fup_embedddings.npy', duties_embeddings)


if __name__ == '__main__':
    skill_extr_obj = SkillExtractor()
    with open('epso_data/epso_data.json', 'r', encoding='utf-8') as file:
        data: dict = json.load(file)
    
    data = skill_extr_obj.load_profiles(data)
    # data = data.iloc[:100]

    skill_extr_obj.calculate_embeddings(data)

    skill_extr_obj.extract(data, extract_path='epso_data/epso_data_skills.json')


        

        

        
    
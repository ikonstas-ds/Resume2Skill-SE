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
    def __init__(self, esco_data_path='data/ESCO/skills_en.csv', model_name='all-mpnet-base-v2', dim=768, nlist=100):
        
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load sentence transformer model
        self.model = SentenceTransformer('sentence-transformers/' + model_name, device=device)

        # Load ESCO skills file
        self.esco_data = pd.read_csv(esco_data_path)
        self.skills_list = self.esco_data.description.values.tolist()
        skill_labels_list = self.esco_data.preferredLabel.values.tolist()
        self.skills_list = [self.skills_list[i]+".\n"+skill_labels_list[i] for i in range(self.esco_data.shape[0])]

        #Create embedding index
        esco_embeddings_path = 'data/ESCO/esco_embedddings.npy'
        if not os.path.exists(esco_embeddings_path):
            self.embeddings_esco = self.model.encode(self.skills_list, show_progress_bar=True)
            self.emb_index = {skill: self.embeddings_esco[i] for i, skill in enumerate(self.skills_list)}
            np.save(esco_embeddings_path, self.embeddings_esco)
        else:
            self.embeddings_esco = np.load('data/ESCO/esco_embedddings.npy')
        
        
        # Faiss initialisation for indexing embeddings
        self.dim = dim
        self.nlist = nlist
        quantizer = faiss.IndexFlatL2(dim)  # the other index
        self.index = faiss.IndexIVFFlat(quantizer, dim, nlist)
        assert not self.index.is_trained
        self.index.train(self.embeddings_esco)
        assert self.index.is_trained

        self.index.add(self.embeddings_esco)
    

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
    

    def extract(self, data, topk=10, extract_path=None):
        experiences_embeddings = np.load('data/experiences_embedddings.npy')

        if type(data) == str:
            with open(data, 'r', encoding='utf-8') as file:
                data: dict = json.load(file)

        
        D, ids = self.index.search(experiences_embeddings, topk)

        data['skills'] = pd.Series(data.index).apply(lambda i: ids[i])

        q = data.groupby('ID')
        prof_skills = []
        for frm_id, item in tqdm(q):
            counts = Counter(flatten(item.skills.tolist()))
            el = [{'ID': frm_id, 'SKILL_ID': int(item[0]), 'WEIGHT': item[1]} for item in list(counts.items())]
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

        print('Calculating embeddings for experience descriptions')
        a = time.time()
        experience_embeddings = self.model.encode(data['experience_description'].tolist(), device=device, show_progress_bar=True)
        print(f'Calculation finished in {(time.time()-a)/3600} hours')


        np.save('data/experiences_embedddings.npy', experience_embeddings)


if __name__ == '__main__':
    skill_extr_obj = SkillExtractor()
    with open('data/extracted_resumes.json', 'r', encoding='utf-8') as file:
        data: dict = json.load(file)
    
    data = pd.DataFrame(data['experiences'])
    # data = data.iloc[:100]

    if not os.path.exists('data/experiences_embedddings.npy'):
        skill_extr_obj.calculate_embeddings(data)

    skill_extr_obj.extract(data, topk=10, extract_path='data/resume_skills.json')


        

        

        
    
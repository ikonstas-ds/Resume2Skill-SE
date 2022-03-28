# import imp
from typing import final
from jmespath import search
from transformers import TopKLogitsWarper
from graphservice.neoservice import neoconnection
from sentence_transformers import SentenceTransformer, util
# import torch
import json
import pandas as pd
import numpy as np
from evaluation.calculate_metrics import MetricsCalculator
from graphservice.search import search_similar_profiles
from tqdm import tqdm


# Load sentence transformer model
# model_name='all-mpnet-base-v2'
# model = SentenceTransformer('sentence-transformers/' + model_name) #, device=device)


class Evaluator():

    def __init__(self, model_name='all-mpnet-base-v2') -> None:
        self.model = SentenceTransformer('sentence-transformers/' + model_name) #, device=device)
        self.rel_scores = None

        with open('data/extracted_resumes.json', 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
        
        data = pd.DataFrame(data['experiences'])
        data.reset_index(inplace=True)
        data.rename(columns={'index':'ind'}, inplace=True)

        exp_embeddings = np.load('data/experiences_embedddings.npy')
        data['emb'] = data.apply(lambda row: exp_embeddings[row[0]], axis=1)
        self.data = data

        

    def get_source_relevance_scores(self, sourceId, targetIds):
        
        # Get source profile duties information
        tx = neoconnection.graph.auto(readonly=True)
        statement = """
        MATCH (n {ID:$sourceId})-[:HAS_EXPERIENCE]-(exp)
        MATCH (exp)-[:HAS_DESCRIPTION]-(dut)
        RETURN n.ID as ID, dut.experience_description as experience_description
        """
        params = {'sourceId': sourceId}

        new_node = tx.run(statement, params)
        source_info = new_node.to_data_frame()

        # Get target profiles duties information
        tx = neoconnection.graph.auto(readonly=True)
        statement = """
        MATCH (n)-[:HAS_EXPERIENCE]-(exp)
        MATCH (exp)-[:HAS_DESCRIPTION]-(dut)
        WHERE n.ID in $targetIds
        RETURN n.ID as ID, dut.experience_description as experience_description
        """
        params = {'targetIds': targetIds}
        # print(targetIds)

        new_node = tx.run(statement, params)
        res = new_node.to_data_frame()

        # src_duty_embeddings = self.model.encode(source_info['experience_description'], show_progress_bar=True)
        # trg_duty_embeddings = self.model.encode(res['experience_description'], show_progress_bar=True)

        # print(trg_duty_embeddings.shape)

        src_duty_embeddings= self.data[self.data['ID'].isin([sourceId])]['emb'].values
        src_duty_embeddings = np.stack(src_duty_embeddings)
        # print(src_duty_embeddings.shape)
        # src_duty_embeddings = torch.from_numpy(src_duty_embeddings)
        trg_duty_embeddings = self.data[self.data['ID'].isin(targetIds)]['emb'].values
        # print(type(trg_duty_embeddings))
        # print(trg_duty_embeddings)
        # trg_duty_embeddings = torch.from_numpy(trg_duty_embeddings)
        trg_duty_embeddings = np.stack(trg_duty_embeddings)
        # print(trg_duty_embeddings.shape)

        cosine_scores = util.pytorch_cos_sim(trg_duty_embeddings, src_duty_embeddings)
        # print(cosine_scores)
        max_cos_scores = cosine_scores.max(axis=1).values.tolist()
        res['cos_scores'] = max_cos_scores

        rel_scores = res.groupby('ID').mean()['cos_scores']
        rel_scores = rel_scores.reset_index().rename(columns={'ID':'targetId', 'cos_scores':'relevance'})
        
        multiplied_sourceId = [sourceId]*rel_scores.shape[0]
        rel_scores.insert(loc=0, column='sourceId', value=multiplied_sourceId)

        # self.rel_scores = rel_scores
        return rel_scores

    
    def get_sim_profiles_results(self, sourceIds, evaluation_path, test_name, sim_score_formula='formula4',
                                no_cross_sector=False, topk=30):

        total_res = []
        for sourceId in tqdm(sourceIds):
            res = search_similar_profiles(**{'sourceId':sourceId, 'sim_score':sim_score_formula,
                                            'no_cross_sector':no_cross_sector, 'topk':topk})
            targetIds = [item['profile']['ID'] for item in res]
            total_res.append({'source_id':sourceId, 'results':targetIds})
        
        test_scores = self.evaluate_results(total_res, evaluation_path, test_name, topk=topk)
        return test_scores
        

    def evaluate_results(self, results_path, evaluation_path, test_name, topk=10):
        """
        :params
        results_path: Input should be a json file with ranking results for each query
                    example = [{'source_id':'<ID>', 'results': ['prof_id1','prof_id2',...],
                                time: <timeinseconds>}, {...},...]
        """

        if type(results_path) == str:
            with open(results_path, 'r', encoding='utf-8') as file:
                results: dict = json.load(file)
        else:
            results = results_path
            
        # print(results)
        final_rels = pd.DataFrame(columns=['sourceId', 'targetId', 'relevance'])
        for result in results:
            sourceId = result['source_id']
            targetIds = result['results']

            rels = self.get_source_relevance_scores(sourceId, targetIds)
            final_rels = pd.concat([final_rels, rels])
        
        final_rels.drop_duplicates(subset=['sourceId', 'targetId'], inplace=True)
        final_rels.set_index(['sourceId', 'targetId'], inplace=True)
        
        metrics_obj = MetricsCalculator(final_rels, results, test_name)

        q1 = metrics_obj.map_adcg_scores(k=topk)
        q2 = metrics_obj.mean_reciprocal_rank()

        test_scores = metrics_obj.save_results(evaluation_path)

        return test_scores


if __name__ == '__main__':
    df = pd.read_csv('data/Resume.csv')
    df_shuf = df.sample(frac=1, random_state=2022).reset_index(drop=True)
    
    df_final = pd.DataFrame()
    for categ, item in df_shuf.groupby('Category'):
        df_final = pd.concat([df_final, item.iloc[:10]])
    
    frm_ids = df_final['ID'].values.tolist()
    
    evl = Evaluator()

    topk_skills = 10  # This depends on the topk number of skills extracted by the SkillExtractor
    formulas = [f'formula{str(i+1)}' for i in range(4)]
    cross_sector_options = [False, True]
    for option in cross_sector_options:
        no_cross_sector = "no_cross_sector" if option else ""
        for formula in formulas:
            
            print(formula+no_cross_sector)
            test_scores = evl.get_sim_profiles_results(sourceIds=frm_ids, evaluation_path='tests/results.csv',
                                    test_name=f'top{str(topk_skills)}_{formula}_{no_cross_sector}', sim_score_formula=formula,
                                    no_cross_sector=option, topk=10)



         













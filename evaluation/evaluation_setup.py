import imp
from typing import final
from jmespath import search
from transformers import TopKLogitsWarper
from graphservice.neoservice import neoconnection
from sentence_transformers import SentenceTransformer, util
import json
import pandas as pd
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
        

    def get_source_relevance_scores(self, sourceId, targetIds):
        
        # Get source profile duties information
        tx = neoconnection.graph.auto(readonly=True)
        statement = """
        MATCH (n {frm_id:$sourceId})-[:HAS_EXPERIENCE]-(exp)
        MATCH (exp)-[:HAS_DUTIES]-(dut)
        RETURN n.frm_id as frm_id, dut.duties as duties
        """
        params = {'sourceId': sourceId}

        new_node = tx.run(statement, params)
        source_info = new_node.to_data_frame()

        # Get target profiles duties information
        tx = neoconnection.graph.auto(readonly=True)
        statement = """
        MATCH (n)-[:HAS_EXPERIENCE]-(exp)
        MATCH (exp)-[:HAS_DUTIES]-(dut)
        WHERE n.frm_id in $targetIds
        RETURN n.frm_id as frm_id, dut.duties as duties
        """
        params = {'targetIds': targetIds}

        new_node = tx.run(statement, params)
        res = new_node.to_data_frame()

        src_duty_embeddings = self.model.encode(source_info['duties'], show_progress_bar=True)
        trg_duty_embeddings = self.model.encode(res['duties'], show_progress_bar=True)

        cosine_scores = util.pytorch_cos_sim(trg_duty_embeddings, src_duty_embeddings)
        max_cos_scores = cosine_scores.max(axis=1).values.tolist()
        res['cos_scores'] = max_cos_scores

        rel_scores = res.groupby('frm_id').mean()['cos_scores']
        rel_scores = rel_scores.reset_index().rename(columns={'frm_id':'targetId', 'cos_scores':'relevance'})
        
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
            targetIds = [item['profile']['frm_id'] for item in res]
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
            
        print(results)
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


         













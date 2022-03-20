import json
import pandas as pd
import numpy as np

# Code for calculating the mean average precision (MAP) and the average discounted cumulative gain (ADCG)

# Load qrels
# After feedback from EPSO on relevances, we will keep a file with pairs of query ids and profile ids
# qrels = pd.read_csv('<qrels>.csv')




# Input should be a json file with ranking results for each query
# example = [{'query_id':'<ID>', results: ['prof_d1','prof_id2',...], time: <timeinseconds>}, {...},...]



# with open('<JSON-FILE>') as f:
#     data = json.load(f)

# modelName = "<NAME>"


class MetricsCalculator():

    def __init__(self, qrelspath, datapath, modelName=None) -> None:
        if type(datapath)==str:    
            with open(datapath) as f:
                self.data = json.load(f)
        else:
            self.data = datapath
            
        self.modelName = modelName
        if type(datapath)==str:
            self.qrels = pd.read_csv(qrelspath)
        else:
            self.qrels = qrelspath
        self.map = None
        self.adcg = None
    
    
    def find_rel(self, query_id, prof_id):
        w = self.qrels.loc[query_id, prof_id].relevance
        return w


    def find_query_rels(self, query_id):
        w = self.qrels.loc[query_id, :].relevance.tolist()
        return w


    def map_adcg_scores(self, k=10):
        
        queries_map = np.zeros(len(self.data))
        queries_adcg = np.zeros(len(self.data))

        for j, query in enumerate(self.data):
            # For each query
            map_score_j = 0
            acdg_score_i = 0

            k = min(k, len(query['results']))
            for i in range(k):
                # For each number k compute the precision
                map_score_i = 0
                rel_i = self.find_rel(query['source_id'], query['results'][i])
                for m in range(i):
                    # for each 
                    map_rel_doc = self.find_rel(query['source_id'], query['results'][m])
                    map_score_i += map_rel_doc

                map_score_j += rel_i*map_score_i / (i+1)
                acdg_score_i += rel_i/np.log2(i+2)

            queries_map[j] = map_score_j / k
            queries_adcg[j] = acdg_score_i
            self.map, self.adcg = queries_map.mean(), queries_adcg.mean()
        return self.map, self.adcg


    def mean_reciprocal_rank(self):
        # Mean Reciprocal Rank (MRR) considers relevance as a binary value (0 or 1)
        rank_scores = [self.find_query_rels(query['source_id']) for query in self.data]
        rs = (np.asarray(r).nonzero()[0] for r in rank_scores)
        self.mrr = np.mean([1. / (r[0] + 1) if r.size else 0. for r in rs])
        return  self.mrr
    

    def save_results(self, results_path):

        # Final computation of map and adcg
        df = pd.DataFrame([[self.map, self.adcg, self.mrr]], index=[self.modelName], columns=['MAP', 'ADCG', 'MRR'])

        # This part is for putting the results of each approach we test in a single file
        try:
            q = pd.read_csv(results_path, index_col=0)
            q = pd.concat([q,df])
        except:
            q = df

        q.to_csv(results_path)
        return q










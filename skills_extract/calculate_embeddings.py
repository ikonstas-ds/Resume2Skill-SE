import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('sentence-transformers/' + 'all-mpnet-base-v2')

with open('epso_data.json', 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

if __name__ == '__main__':

    df_exp = pd.DataFrame(data['experiences'])
    df_fup =  pd.DataFrame(data['follow_up_answers'])

    df_exp = df_exp[['FRM_ID', 'DUTIES']]
    df_fup = df_fup[['FRM_ID', 'FOLLOW_UP_ANSWER']]
    df_fup.rename(columns={'FOLLOW_UP_ANSWER': 'DUTIES'}, inplace=True)

    data = pd.concat([df_exp, df_fup])

    duties_embeddings = model.encode(data['DUTIES'].tolist(), show_progress_bar=True)


    np.save('epso_data/duties_fup_embedddings.npy', duties_embeddings)

import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('sentence-transformers/' + 'all-mpnet-base-v2')

with open('data/extracted_resumes.json', 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

if __name__ == '__main__':

    df_exp = pd.DataFrame(data['experiences'])

    experience_embeddings = model.encode(df_exp['experience_description'].tolist(), show_progress_bar=True)


    np.save('data/experiences_embedddings.npy', experience_embeddings)

from lib2to3.pgen2.token import OP
# from msilib.schema import Feature
from pydantic import BaseModel, Field, conlist
from typing import Optional, List
from enum import Enum


class TagsQuery(BaseModel):
    texts: List[str] = Field(
        ...,
        title="A list of texts to be tagged",
        description="Texts can be whole CVs, the different experiences of a same person..."
    )
    num_tags: Optional[int] = Field(
        3,
        title="Number of tags",
        description="Number of tags to return for each text.",
        gte=1,
        lte=10
    )
    min_score: Optional[float] = Field(
        None,
        title="Minimum score for each tag",
        description="Tags with a score less than this value won't be returned."
    )


class Tagging(BaseModel):
    tags: List[List[str]] = Field(
        ...,
        title="Tags",
        description="A list of tag lists, one for each text submitted, in the same order."
    )
    scores: List[List[float]] = Field(
        ...,
        title="Scores",
        description="A list of score lists, matching each tag returned."
    )


class DistanceType(str, Enum):
    euclidean = "euclidean"
    minkowski = "minkowski"
    cityblock = "cityblock"
    sqeuclidean = "sqeuclidean"
    cosine = "cosine"
    correlation = "correlation"
    hamming = "hamming"
    jaccard = "jaccard"
    chebyshev = "chebyshev"
    canberra = "canberra"


class SemanticQuery(BaseModel):
    text_pairs: List[conlist(item_type=str, min_items=2, max_items=2)] = Field(
        ...,
        title="Text pairs",
        description="An array of arrays of two texts.",
        example=[
          [
            'Weather is really bad today.',
            'It has been raining all day.'
          ],
          [
            'It has been raining all day.',
            'I am going to the cinema.'
          ]
        ]
    )
    distance_type: Optional[DistanceType] = Field(
        "euclidean",
        title="Distance type",
        description="Optional. The name of a metric to perform the distance calculation. Defaults to \"euclidean\" if "
                    "not specified. See also /get-semantic-metrics. "
    )


class OverlapQuery(BaseModel):
    term: str = Field(
        ...,
        title="Term",
        description="Term on which to make the similarity search."
    )


class KeywordsQuery(BaseModel):
    text: str = Field(
        ...,
        title="Text",
        description="A text from which to extract keywords."
    )


class ProfileQuery(BaseModel):
    profile_id: int = Field(
        ...,
        title="Profile ID",
        description="Profile ID from which to identify similar profiles"
    )
    score_formula: Optional[str] = Field(
        "formula2",
        title="Similarity score formula",
        description="Optional. The name of the formula to perform the similarity score. Defaults to \"formula2\" if "
                    "not specified. "
                    "formula1: Sum(source_profile_skill_weights + Sum(target_profile_skill_weights)"
                    "formula2: Sum(source_profile_skill_weights*target_profile_skill_weights)"
                    "formula3: Count(number_of_common_skills)"
                    "formula4: (Count(number_of_common_skills)^2)/(Count(number_of_source_skills)*Count(number_of_target_skills))"
    )
    no_cross_sector: Optional[bool] = Field(
        None,
        title="Similarity score",
        description="Filter to not consider cross-sector skills from ESCO"
    )
    topk: Optional[int] = Field(
        None,
        title="Limit results",
        description="The maximum number of relevant profiles to retrieve."
                    "If not specified, the top 30 profiles are considered."
    )


class ProfileIDsQuery(BaseModel):
    frm_ids: List[int] = Field(
        ...,
        title="A list of profile IDs",
        description="A list of profile IDs (frm_id) to retrieve profile information"
    )
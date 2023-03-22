from mudpie import score
import json
import os
import pkg_resources


def _load(resource):
    resource_path = os.path.join('.data', resource)
    file_path = pkg_resources.resource_filename('mudpie', resource_path)

    with open(file_path, 'r') as f:
        data = json.load(f)

    return data


def test_score_male():
    answers = _load('test_answers_male.json')
    scores = _load('test_scores_male.json')
    assert score(answers, gender=0) == scores


def test_score_female():
    answers = _load('test_answers_female.json')
    scores = _load('test_scores_female.json')
    assert score(answers, gender=1) == scores

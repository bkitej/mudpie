import json
import os
import pkg_resources


_PRINCIPAL_SCALE_CODES = ('Hs', 'D', 'Hy', 'Pd', 'Pa', 'Pt', 'Sc', 'Ma')
_N_QUESTIONS = 567


def _load(resource):
    resource_path = os.path.join('.data', resource)
    file_path = pkg_resources.resource_filename('mudpie', resource_path)

    with open(file_path, 'r') as f:
        data = json.load(f)

    return data


rin = _load('rin.json')
scales = _load('scales.json')
_questions_internal = _load('questions.json')
questions = _questions_internal[1:]  # strip header


def _js_get(lst, index):
    """Mimic JavaScript's out-of-bounds undefined indexing behavior."""

    try:
        val = lst[int(index)]
    except IndexError:
        val = None
    return val


def _preprocess_answers(answers):
    """The source this script is adapted from accepts questions as 1-indexed and
    uses "T"/"F" strings parsed from radio buttons on the input form.
    """

    tf_map = {True: 'T', 'T': 'T', False: 'F', 'F': 'F'}
    answers = [tf_map.get(x, '?') for x in answers]
    if len(answers) == _N_QUESTIONS:
        answers = [None] + answers
    return answers


def _to_scale_row(scale, desc, raw_score, k_score, t_score, pct_answered):
    return {
        'scale_code': scale,
        'scale_name': desc,
        'raw_score': raw_score,
        'k_score': k_score,
        't_score': t_score,
        'pct_answered': pct_answered,
    }


def _to_ci_row(scale, desc, question, answer, text):
    return {
        'scale_code': scale,
        'scale_name': desc,
        'question': question,
        'answer': answer,
        'text': text,
    }


def score(answers, gender):
    f"""
    Calculates the MMPI-2 score based on the given answers and gender.

    Args:
        answers (list): A list of answers (True/False) with a length equal to {_N_QUESTIONS}.
        gender (int): A value of 0 for male or 1 for female.

    Raises:
        ValueError: If the number of input answers is not equal to {_N_QUESTIONS}.

    Returns:
        dict: A dictionary containing the following keys:
            - 'scale_table': A list of dictionaries with scale scores.
            - 'ci_table': A list of dictionaries with clinical indicator information.
            - 'pe': The overall profile elevation.
    """

    if len(answers) != _N_QUESTIONS:
        raise ValueError(f'Invalid number of input answers: {len(answers)}')

    answers = _preprocess_answers(answers)

    scale_table = []
    ci_table = []

    t_cnt = answers.count('T')
    f_cnt = answers.count('F')
    cs_cnt = answers.count('?')

    scale_table.append(
        _to_scale_row(
            'True', None, t_cnt, None, None, t_cnt * 100 / _N_QUESTIONS
        )
    )
    scale_table.append(
        _to_scale_row(
            'False', None, f_cnt, None, None, f_cnt * 100 / _N_QUESTIONS
        )
    )
    scale_table.append(
        _to_scale_row(
            '?', None, cs_cnt, None, None, cs_cnt * 100 / _N_QUESTIONS
        )
    )

    for i in range(len(rin)):
        rawscore = rin[i][0][2]

        for j in range(len(rin[i][1])):
            rp = rin[i][1][j]

            if answers[rp[0]] == rp[1] and answers[rp[2]] == rp[3]:
                rawscore += rp[4]

        scale_table.append(
            _to_scale_row(
                rin[i][0][0],
                rin[i][0][1],
                rawscore,
                None,
                rin[i][2 + gender][rawscore],
                None,
            )
        )

    k = 0
    pe = 0

    for i in range(len(scales)):
        n = 0
        rawscore = 0
        tscale = scales[i][3 + gender]
        for j in range(len(scales[i][1])):
            q = scales[i][1][j]

            if answers[q] == 'T':
                n += 1
                rawscore += 1

                if tscale is None:
                    ci_table.append(
                        _to_ci_row(
                            scales[i][0][1],
                            scales[i][0][2],
                            q,
                            'True',
                            _questions_internal[q],
                        )
                    )

            elif answers[q] == 'F':
                n += 1

        for j in range(len(scales[i][2])):
            q = scales[i][2][j]

            if answers[q] == 'F':
                n += 1
                rawscore += 1

                if tscale is None:
                    ci_table.append(
                        _to_ci_row(
                            scales[i][0][1],
                            scales[i][0][2],
                            q,
                            'False',
                            _questions_internal[q],
                        )
                    )

            elif answers[q] == 'T':
                n += 1

        if tscale is not None:
            if scales[i][0][0] == 'K':
                k = rawscore

            if _js_get(tscale, 0):
                kscore = k * tscale[0] + rawscore
                kscore = round(kscore)
                tscore = tscale[kscore + 1]
            else:
                kscore = None
                tscore = _js_get(tscale, rawscore + 1)

            percent = n * 100 / (len(scales[i][1]) + len(scales[i][2]))
            scale_table.append(
                _to_scale_row(
                    scales[i][0][1],
                    scales[i][0][2],
                    rawscore,
                    kscore,
                    tscore,
                    percent,
                )
            )

            if scales[i][0][1] in _PRINCIPAL_SCALE_CODES:
                pe += tscore

    pe /= 8
    return {
        'scale_table': scale_table,
        'ci_table': ci_table,
        'pe': pe,
    }


__all__ = [
    'questions',
    'rin',
    'scales',
    'score',
]

## This library scores psych test answers.

Adapted from: http://www.ohiofamilyrights.com/docs/MMPI_scoring.html

Usage: 

```
from mudpie import questions, score
import pandas as pd

if respondent_is_male():
    gender = 0
else:
    gender = 1
answers = [answer_the_question(q) for q in questions]
scores = score(answers, gender)

scales = pd.DataFrame(scores['scale_table'])
critical_items = pd.DataFrame(scores['ci_table'])
profile_elevation = scores['pe']
```
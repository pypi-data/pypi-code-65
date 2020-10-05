from flask_login import current_user
from hemlock import Debug as D, Embedded, Input, Page, Submit as S, Validate as V

CORRECT_1 = 25
CORRECT_2A = 30
CORRECT_2B = 20
CORRECT_3 = 50

def berlin(require=False):
    """
    Add the Berlin Numeracy Test to a hemlock survey.

    Parameters
    ----------
    require : bool, default=False
        Indicates that responses are required.

    Returns
    -------
    Question 1 : hemlock.Page
        The first page of the Berlin Numeracy Test.

    Notes
    -----
    Although this function returns only the first page of the test, it is all
    you need to add the full test to your survey. The submit function of the 
    page returned by this function adaptively generates additional pages of 
    the test.
    """
    return Page(
        Input(
            '''
            <p>Out of 1,000 people in a small town 500 are members of a 
            choir. Out of these 500 members in the choir 100 are men. Out 
            of the 500 inhabitants that are not in the choir 300 are men. 
            What is the probability that a randomly drawn man is a member 
            of the choir? Please enter the probability as a percent.</p>
            ''',
            append='%', 
            type='number', min=0, max=100, step='any', required=require,
            var='Berlin1', data_rows=-1,
            submit=S(_verify1, require),
            debug=[D.send_keys(), D.send_keys('25', p_exec=.5)]
        ),
        name='Berlin 1', 
        timer=('Berlin1Time', -1),
        debug=[D.debug_questions(), D.forward()]
    )

def _verify1(q1, require):
    if q1.data != CORRECT_1:
        page = Page(
            Input(
                '''
                <p>Imagine we are throwing a five-sided die 50 times. On 
                average, out of these 50 throws how many times would this 
                five-sided die show an odd number (1, 3, or 5)?</p>
                ''',
                append='out of 50 throws',
                type='number', min=0, max=50, step=1, required=require,
                var='Berlin2a', data_rows=-1,
                submit=_verify2a,
                debug=[D.send_keys(), D.send_keys('30', p_exec=.5)]
            ),
            name='Berlin 2a', 
            timer=('Berlin2aTime', -1),
            debug=[D.debug_questions(), D.forward()]
        )
    else:
        page = Page(
            Input(
                '''
                <p> Imagine we are throwing a loaded die (6 sides). The 
                probability that the die shows a 6 is twice as high as the 
                probability of each of the other numbers. On average, out 
                of these 70 throws how many times would the die show the 
                number 6?</p>
                ''', 
                append='out of 70 throws',
                type='number', min=0, max=70, required=require,
                var='Berlin2b', data_rows=-1,
                submit=S(_verify2b, require),
                debug=[D.send_keys(), D.send_keys('20', p_exec=.2)]
            ),
            name='Berlin 2b (or not 2b?)', 
            timer=('Berlin2bTime', -1),
            debug=[D.debug_questions(), D.forward()]
        )
    q1.branch.pages.insert(q1.page.index+1, page)

def _verify2a(q2a):
    _record_score(q2a, score=2 if q2a.data == CORRECT_2A else 1)

def _record_score(question, score):
    """
    Record the Berlin score as embedded data and make the score accessible
    through `current_user.g['BerlinScore']`.
    """
    question.page.embedded = [Embedded('BerlinScore', score, data_rows=-1)]
    current_user.g['BerlinScore'] = score

def _verify2b(q2b, require):
    if q2b.data == CORRECT_2B:
        _record_score(q2b, score=4)
    else:
        page = Page(
            Input(
                '''
                <p>In a forest 20% of mushrooms are red, 50% brown, and 30% 
                white. A red mushroom is poisonous with a probability of 
                20%. A mushroom that is not red is poisonous with a 
                probability of 5%. What is the probability that a poisonous 
                mushroom in the forest is red?</p>
                ''',
                append='%', 
                type='number', min=0, max=100, step='any', required=require,
                var='Berlin3', data_rows=-1,
                submit=_verify3,
                debug=[D.send_keys(), D.send_keys('50', p_exec=.5)]
            ),
            name='Berlin 3', 
            timer=('Berlin3Time', -1),
            debug=[D.debug_questions(), D.forward()]
        )
        q2b.branch.pages.insert(q2b.page.index+1, page)

def _verify3(q3):
    _record_score(q3, score=3 if q3.data != CORRECT_3 else 4)
#!/usr/bin/python




def apply_correction(hyp, scores, c1, c2, method="min"):
    """

    """
    if method == "min":
        hyp = apply_correction_min(hyp, scores, c1, c2)
    elif method == "max":
        hyp = apply_correction_max(hyp, scores, c1, c2)
    elif method == "average":
        hyp = apply_correction_avr(hyp, scores, c1, c2)

    return hyp


def apply_correction_min(hyp,scores,c1,c2):
    c1list=[]
    c2list=[]

    for i in range(len(hyp)):
        if i!=c1 and hyp[i]['cluster'] == hyp[c1]['cluster']:
            c1list.append(i)
        if i!=c2 and hyp[i]['cluster'] == hyp[c2]['cluster']:
            c2list.append(i)

    if len(c1list)==0 and len(c2list)!=0:
        c2_to_c1 = True

    elif len(c2list)==0 and len(c1list)!=0:
        c2_to_c1 = False

    elif len(c1list)==0 and len(c2list)==0:
        c2_to_c1 = True

    else:
        c1dist = []
        c2dist = []
        for i in range(len(c1list)):
            c1dist.append(scores.scoremat[c1][c1list[i]])
        for i in range(len(c2list)):
            c2dist.append(scores.scoremat[c2][c2list[i]])
        if min(c2dist) <  min(c1dist):
            c2_to_c1 = True
        else:
            c2_to_c1 = False

    if c2_to_c1:
        hyp[c1]['cluster'] = hyp[c2]['cluster']
    else:
        hyp[c2]['cluster'] = hyp[c1]['cluster']
    return hyp




def apply_correction_max(hyp,scores,c1,c2):
    c1list=[]
    c2list=[]

    for i in range(len(hyp)):
        if i!=c1 and hyp[i]['cluster'] == hyp[c1]['cluster']:
            c1list.append(i)
        if i!=c2 and hyp[i]['cluster'] == hyp[c2]['cluster']:
            c2list.append(i)

    if len(c1list)==0 and len(c2list)!=0:
        c2_to_c1 = True

    elif len(c2list)==0 and len(c1list)!=0:
        c2_to_c1 = False

    elif len(c1list)==0 and len(c2list)==0:
        c2_to_c1 = True

    else:
        c1dist = []
        c2dist = []
        for i in range(len(c1list)):
            c1dist.append(scores.scoremat[c1][c1list[i]])
        for i in range(len(c2list)):
            c2dist.append(scores.scoremat[c2][c2list[i]])
        if max(c2dist) <  max(c1dist):
            c2_to_c1 = True
        else:
            c2_to_c1 = False

    if c2_to_c1:
        hyp[c1]['cluster'] = hyp[c2]['cluster']
    else:
        hyp[c2]['cluster'] = hyp[c1]['cluster']
    return hyp

def apply_correction_avr(hyp,scores,c1,c2):
    c1list=[]
    c2list=[]

    for i in range(len(hyp)):
        if i!=c1 and hyp[i]['cluster'] == hyp[c1]['cluster']:
            c1list.append(i)
        if i!=c2 and hyp[i]['cluster'] == hyp[c2]['cluster']:
            c2list.append(i)

    if len(c1list)==0 and len(c2list)!=0:
        c2_to_c1 = True

    elif len(c2list)==0 and len(c1list)!=0:
        c2_to_c1 = False

    elif len(c1list)==0 and len(c2list)==0:
        c2_to_c1 = True

    else:
        c1dist = []
        c2dist = []
        for i in range(len(c1list)):
            c1dist.append(scores.scoremat[c1][c1list[i]])
        for i in range(len(c2list)):
            c2dist.append(scores.scoremat[c2][c2list[i]])
        if sum(c2dist)/float(len(c2dist)) <  sum(c1dist)/float(len(c1dist)):
            c2_to_c1 = True
        else:
            c2_to_c1 = False

    if c2_to_c1:
        hyp[c1]['cluster'] = hyp[c2]['cluster']
    else:
        hyp[c2]['cluster'] = hyp[c1]['cluster']
    return hyp


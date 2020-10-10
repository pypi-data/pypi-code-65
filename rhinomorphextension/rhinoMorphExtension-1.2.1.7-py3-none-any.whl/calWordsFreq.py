from collections import Counter
import importlib
rhino_spec = importlib.util.find_spec('rhinoMorph')     # 이 부분을 rhinoMorph3, rhinoMorph4 처럼 사용버전만을 위한 것으로 지정할 수 있다
found = rhino_spec is not None

if found:
    import rhinoMorph as rhinoMorph
elif not found:
    rhino_spec = importlib.util.find_spec('rhinoMorph')
    found = rhino_spec is not None

    if found:
        import rhinoMorph as rhinoMorph
    else:
        print("Package Does Not Exists Error: Please install rhinoMorph (pip install rhinoMorph)")

rn = rhinoMorph.startRhino()
####################################################################################################
def write_data(data, filename, encoding='cp949'):
  '''파일에 저장합니다'''
  with open(filename, 'w', encoding=encoding) as f:
    f.write(data)


def getNounVerb(rhinoMorph, rn, data, eomi=True, combineN=False):
    '''명사류와 동사류를 가지고 옵니다'''
    morphed_data_NNGNNP = ''
    morphed_data_VVVAXR = ''

    for data_each in data:
        morphs, poses = rhinoMorph.wholeResult_list(rn, data_each, eomi=eomi, combineN=combineN)
        NNGNNP = []
        VVVAXR = []

        for i, pose in enumerate(poses):
            if ((pose == 'NNG') or (pose == 'NNP') or (pose == 'NP') or (pose == 'XR')):
                NNGNNP.append(morphs[i]+' ')            # 태그가 NNG 또는 NNP 일 때의 형태만을 가져온다
            elif (pose == 'VV') or (pose == 'VA') or (pose == 'XR') or (pose == 'VX') or (pose == 'VCP') or (pose == 'VCN'):
                VVVAXR.append(morphs[i]+' ')            # 태그가 위의 목록일 때의 형태만을 가져온다

        joined_data_each_NNGNNP = ' '.join(NNGNNP)      # 문자열을 하나로 연결
        joined_data_each_VVVAXR = ' '.join(VVVAXR)      # 문자열을 하나로 연결

        if joined_data_each_NNGNNP:                     # 내용이 있는 경우만 저장하게 함
            morphed_data_NNGNNP += joined_data_each_NNGNNP
        if joined_data_each_VVVAXR:                     # 내용이 있는 경우만 저장하게 함
            morphed_data_VVVAXR += joined_data_each_VVVAXR

    return morphed_data_NNGNNP, morphed_data_VVVAXR


def calNounVerb(data, eomi=True, combineN=False):
    '''데이터에서 명사류와 동사류의 빈도를 구합니다'''
    nouns, verbs = getNounVerb(rhinoMorph, rn, data, eomi=eomi, combineN=combineN)

    # 명사류 처리
    mergedNounsList = nouns.split(' ')               # 결합된 요소들을 공백 단위로 분리하여 하나의 리스트로 만든다
    mergedNounsList = filter(None, mergedNounsList)  # null 값 제거
    wordInfo_noun = Counter(mergedNounsList)         # 하나의 리스트로 결합된 요소를 카운트한다 (내림차순)

    # 동사류 처리
    mergedVerbsList = verbs.split(' ')               # 결합된 요소들을 공백 단위로 분리하여 하나의 리스트로 만든다
    mergedVerbsList = filter(None, mergedVerbsList)  # null 값 제거
    wordInfo_verb = Counter(mergedVerbsList)         # 하나의 리스트로 결합된 요소를 카운트한다 (내림차순)

    # wordInfo.get의 출력된 값을 기준으로 wordInfo를 정렬한다
    sorted_wordInfo_noun = sorted(wordInfo_noun, key=wordInfo_noun.get, reverse=True)
    sorted_wordInfo_noun_values = sorted(wordInfo_noun.values(), reverse=True)
    sorted_wordInfo_verb = sorted(wordInfo_verb, key=wordInfo_verb.get, reverse=True)
    sorted_wordInfo_verb_values = sorted(wordInfo_verb.values(), reverse=True)

    # 정렬된 내용으로 다시 딕셔너리를 만든다
    ordered_nouns = dict(zip(sorted_wordInfo_noun, sorted_wordInfo_noun_values))
    ordered_verbs = dict(zip(sorted_wordInfo_verb, sorted_wordInfo_verb_values))

    return ordered_nouns, ordered_verbs

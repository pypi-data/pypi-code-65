# linguatools.py
import numpy as np
import re

def read_data(filename, encoding, start):
    """읽기 함수"""
    with open(filename, 'r', encoding=encoding) as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        data = data[start:]                 # txt 파일의 헤더(id document label) 제외하기는 1:
    return data

def read_data2(filename, encoding, start):
    """읽기 함수. 줄바꿈 엔터만 있었고, 아무 내용이 없는 것은 제외"""
    with open(filename, 'r', encoding=encoding) as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        data = data[start:]                 # txt 파일의 헤더(id document label)는 제외하기는 1:

    data = [d for d in data if len(d) == 1 and d[0] != '']
    return data


def listToString(s, add=''):
    '''리스트 원소를 하나의 문자열로 만듭니다'''
    str = ""
    for ele in s:
        str += ele+add
    return str


def read_data_cols(filename, encoding):
    """읽기 함수. 탭으로 구분된 컬럼이 있는 경우에 사용된다"""
    with open(filename, 'r', encoding=encoding) as f:
        data = [line.split('\t') for line in f.read().splitlines() if line != '']   # 엔터만 있는 줄은 넘어간다
    return data


def write_data(data, filename, encoding="cp949"):
    """쓰기 함수"""
    with open(filename, 'w', encoding=encoding) as f:
        f.write(data)


def makeFlatList(nestedList):
    """중첩리스트를 단일리스트로 변환하는 함수"""
    flatList = []  # nested list를 일반 list로 변형
    for sublist in nestedList:
        for item in sublist:
            flatList.append(item)
    return flatList


def findKeyword(sample_data, flat_termlist):
    """키워드를 찾는 함수"""
    foundKeyword = []
    newidx = -1
    for idx, sample_data_each in enumerate(sample_data):
        if idx < newidx:
            continue

        sample_data_appending = sample_data[idx]
        appended = False

        for termlistidx, termlist_each in enumerate(flat_termlist):
            found = False

            if termlist_each.startswith(sample_data[idx]):          # 현재의 사전표현이 현재의 배열내용으로 시작한다면
                if len(termlist_each) == len(sample_data[idx]):     # 현재의 사전표현과 현재의 배열내용과 길이가 같다면
                    if termlist_each == sample_data[idx]:           # 현재의 사전표현과 현재의 배열내용이 같은 내용이라면
                        #print("완전일치1: " + sample_data[idx] + " - " + termlist_each + " - " + str(idx) + " - " + sample_data[idx])
                        foundKeyword.append(termlist_each)
                        break
                    else:
                        print("never")
                elif len(termlist_each) > len(sample_data[idx]):    # 현재의 사전표현이 현재의 배열내용보다 길이가 길다면
                    # print("부분일치1: " + sample_data[idx] + " - " + termlist_each + " - " + sample_data_appending + " + " + str(idx))

                    if idx < (len(sample_data) - 1):  # 뒤에서 +1을 할 것이므로 여기서 -1 조건을 달아야 한다
                        if termlist_each.startswith(sample_data_appending + sample_data[idx + 1]):
                            if len(termlist_each) == len(sample_data_appending + sample_data[idx + 1]):
                                if termlist_each == sample_data_appending + sample_data[idx + 1]:
                                    sample_data_appending += sample_data[idx + 1]
                                    appended = True
                                    #print("완전일치2: " + sample_data_appending + " - " + termlist_each + " - " + str(idx) + " - " + sample_data[idx])
                                    foundKeyword.append(termlist_each)
                                    found = True
                                    newidx = idx + 2  # loop 내에서는 idx 값이 변동된다
                                    break
                                else:
                                    print("never")

                            elif len(termlist_each) > len(sample_data_appending + sample_data[idx + 1]):
                                # if termlist_each.startswith(sample_data_appending + sample_data[idx + 1]):  # 중복된 조건!!
                                sample_data_appending += sample_data[idx + 1]
                                appended = True
                                # print("부분일치2: " + sample_data[idx] + " - " + sample_data[idx + 1] + " - " + termlist_each + " - " + sample_data_appending)
                                idx = idx + 1  # loop 내에서는 idx 값이 변동된다

                                if appended:  # 부분일치를 이룬 적이 있는 경우에만
                                    for i in range(idx, len(flat_termlist)):
                                        if termlistidx + 1 < (len(flat_termlist)):
                                            if sample_data_appending + sample_data[idx + 1] == flat_termlist[
                                                termlistidx]:
                                                sample_data_appending += sample_data[idx + 1]
                                                #print("완전일치3: " + sample_data_appending + " - " + flat_termlist[termlistidx] + " - " + str(idx) + " - " + sample_data[idx])
                                                foundKeyword.append(flat_termlist[termlistidx])
                                                found = True
                                                break
                                            else:
                                                termlistidx = termlistidx + 1
                    if found:
                        break

                else:  # 현재의 사전표현이 현재의 배열내용보다 길이가 짧다면
                    print("never")

    return foundKeyword


def splitListItems(items, paste=False):
    """리스트 원소의 string을 space 기준으로 다시 원소로 분리합니다
    paste: 공백 단위로 다시 붙여서 하나의 원소를 만들어야 하는 경우"""
    new_items = []
    for item in items:
        if paste:
            item = ' '.join(item)
        new_items.append(item.split())
    return new_items


def substiSentence(morphs, poses, substi, only):
    '''명사와 동사를 찾아 기호로 변환하고, 명사,동사,조사,어미만 붙여 연결한다'''
    noun_list = []
    verb_list = []
    nouns = ''
    verbs = ''

    morph_idx = 0
    noun_idx = 0
    verb_idx = 0
    if substi:          # 명사와 동사는 각각 NOUN과 VERB로 치환한다
        for pos in poses:
            if pos == 'NNG' or pos == 'NNP':
                noun_list.append(morphs[morph_idx])
                morphs[morph_idx] = 'NOUN' + str(noun_idx)
                noun_idx += 1
            elif pos == 'VV' or pos == 'VA' or pos == 'VX' or pos == 'XR':
                verb_list.append(morphs[morph_idx])
                morphs[morph_idx] = 'VERB' + str(verb_idx)
                verb_idx += 1
            morph_idx += 1

    new_data = ''
    if only:            # 명사, 동사, 조사, 어미만 남긴다
        pos_idx = 0
        for morph in morphs:
            if poses[pos_idx] == 'NNG' or poses[pos_idx] == 'NNP' or poses[pos_idx] == 'VV' or poses[pos_idx] == 'VA' or poses[pos_idx] == 'VX' or poses[pos_idx] == 'XR' or poses[pos_idx].startswith('J') or poses[pos_idx].startswith('E'):
                new_data += ' ' + morph + ' '
            pos_idx += 1
    else:               # 모든 어휘를 남긴다
        for morph in morphs:
            new_data += ' ' + morph + ' '

    for noun_each in noun_list:
        nouns += noun_each + ','

    for verb_each in verb_list:
        verbs += verb_each + ','

    return new_data, nouns, verbs


def getSmallNum(num1, num2):
    '''두 개의 수를 비교하여 작은 수를 출력한다'''
    smallNum = 0
    if num1 == num2:
        smallNum = num1
    elif num1 < num2:
        smallNum = num1
    else:
        smallNum = num2
    return smallNum


def isFirstNumSmall(num1, num2):
    '''첫 번째 수가 두 번째 수보다 작은 수임을 확인합니다'''
    ck = False
    if num1 < num2:
        ck = True
    return ck


def delSignContents(text, startSign='(', endSign=')'):
    '''괄호 안의 내용을 삭제한다. 다양한 기호에 대하여 여러 번 나와도 삭제할 수 있도록 해야 한다'''
    start = [i for i, x in enumerate(text) if x == startSign]
    end = [i for i, x in enumerate(text) if x == endSign]

    signNum = getSmallNum(len(start), len(end))     # 두 수 중 작은 수를 반복할 수로 간주한다

    for i in range(signNum):
        start = [i for i, x in enumerate(text) if x == startSign]
        end = [i for i, x in enumerate(text) if x == endSign]

        if(len(start)>0 and len(end)>0):
            if (isFirstNumSmall(start[0], end[0])):  # 첫 번째 수가 두 번째 수보다 작은 것이 맞는 경우에만,
                text = text[:start[0]] + text[end[0] + 1:]

    return text


def getConnectedNoun(rhinoMorph, rn, data):
    '''명사류만을 가지고 옵니다. 단, 어절내 연결된 명사들을 하나로 가지고 옵니다'''
    morphed_data_NNGNNP = ''
    for data_each in data:
        morphs, poses = rhinoMorph.wholeResult_list(rn, data_each, combineN=True)
        NNGNNP = []

        for i, pose in enumerate(poses):
            if ((pose == 'NNG') or (pose == 'NNP')):
                NNGNNP.append(morphs[i]+' ')            # 태그가 NNG 또는 NNP 일 때의 형태만을 가져온다

        joined_data_each_NNGNNP = ' '.join(NNGNNP)      # 문자열을 하나로 연결
        if joined_data_each_NNGNNP:                     # 내용이 있는 경우만 저장하게 함
            morphed_data_NNGNNP += joined_data_each_NNGNNP

    return morphed_data_NNGNNP


def getConnectedVerb(rhinoMorph, rn, data):
    '''동사류만을 가지고 옵니다.'''
    morphed_data_VVVAXR = ''
    for data_each in data:
        morphs, poses = rhinoMorph.wholeResult_list(rn, data_each)
        VVVAXR = []

        for i, pose in enumerate(poses):
            if (pose == 'VV') or (pose == 'VA') or (pose == 'XR'):
                morphs[i] = morphs[i] + '다'
                VVVAXR.append(morphs[i]+' ')            # 태그가 VV, VA, XR일 때의 형태만을 가져온다

        joined_data_each_VVVAXR = ' '.join(VVVAXR)      # 문자열을 하나로 연결
        if joined_data_each_VVVAXR:                     # 내용이 있는 경우만 저장하게 함
            morphed_data_VVVAXR += joined_data_each_VVVAXR

    return morphed_data_VVVAXR


def getNListElement(nested_items, n):
    '''중첩 리스트에서 n번째 요소만 가져옵니다'''
    nListElement = []
    for nested_item in nested_items:
        nListElement.append(nested_item[n])
    return nListElement


def write_data_list(list, filename, encoding):
    """리스트 데이터를 위한 쓰기 함수"""
    with open(filename, 'w', encoding=encoding) as f:
        for item in list:
            if len(item) == 1:
                f.write('%s\n' % (item[0]))
            elif len(item) == 2:
                f.write('%s\t%s\n' % (item[0], item[1]))
            elif len(item) == 3:
                f.write('%s\t%s\t%s\n' % (item[0], item[1], item[2]))
            elif len(item) == 4:
                f.write('%s\t%s\t%s\t%s\n' % (item[0], item[1], item[2], item[3]))
            elif len(item) == 5:
                f.write('%s\t%s\t%s\t%s\t%s\n' % (item[0], item[1], item[2], item[3], item[4]))
            elif len(item) == 6:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (item[0], item[1], item[2], item[3], item[4], item[5]))
            elif len(item) == 7:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (item[0], item[1], item[2], item[3], item[4], item[5], item[6]))
            elif len(item) == 8:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))
            else:
                print("Error in write_data_list!!")
                print(len(item))


def to_one_hot(sequences, dimension):
    """원-핫-인코딩 함수"""
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.
    return results


def change_to_binary(number):
    """라벨을 0과 1로 변환"""
    changed = []
    for n in number:
        if n == 0:
            changed.append(0)
        else:
            changed.append(1)
    return changed


def change_to_int(percent):
    """확률값을 정수로 변환"""
    changed = []
    for p in percent:
        if p > 0.5:
            changed.append(1)
        else:
            changed.append(0)
    return changed


def checkIs(li1, li2):
    "li1 리스트의 내용 일부가 li2 리스트에 있는지를 확인"
    found = False
    li_is = [i for i in li1 if i in li2]
    if li_is != []:
        found = True

    return found


def getTag1(data, prediction):
    '''Tag 1인 데이터만 가져옵니다'''
    line = []

    for idx, data_each in enumerate(data):
        if prediction[idx][0] == 1:
            line.append(data_each)

    return line


def splitFileSentences(rhinoMorph, rn, data, sign=True, cntidx=True):
    '''문장을 분리하고, 인덱스를 붙인다'''
    pattern = re.compile(r"\.|\?|!")
    newdata = []

    idx = 1
    for i, oneline in enumerate(data):
        if len(oneline[0]) > 1:             # 내용이 있는 경우만 진행한다
            if sign:
                onelineArr = pattern.split(oneline[0])
                for onelineArr_each in onelineArr:
                    onelineArr_each = onelineArr_each.strip()
                    if cntidx:
                        newdata.append(str(idx)+'\t'+onelineArr_each)
                        idx += 1
                    else:
                        newdata.append(onelineArr_each)

    newdata = [line.split('\t') for line in newdata]

    return newdata



def splitFileSentences2(rhinoMorph, rn, data, sign=True, cntidx=True):
    '''문장을 분리하고, 인덱스를 붙인다
    0번이 아니라 1번 컬럼을 대상으로 한다'''
    pattern = re.compile(r"\.|\?|!")
    newdata = []
    newdata2 = []

    idx = 1
    for i, oneline in enumerate(data):
        if len(oneline[1]) > 1:             # 내용이 있는 경우만 진행한다
            if sign:
                onelineArr = pattern.split(oneline[1])
                originalIdx = oneline[0]
                originalCol2 = oneline[2]
                originalCol3 = oneline[3]
                originalCol4 = oneline[4]
                originalCol5 = oneline[5]

                for onelineArr_each in onelineArr:
                    onelineArr_each = onelineArr_each.strip()
                    if cntidx:
                        newdata.append(str(idx) + '\t' + onelineArr_each)
                        newdata2.append(str(idx)+'\t'+onelineArr_each+'\t'+originalIdx+'\t'+originalCol2+'\t'+originalCol3+'\t'+originalCol4+'\t'+originalCol5)
                        idx += 1
                    else:
                        newdata.append(onelineArr_each)

    newdata = [line.split('\t') for line in newdata]
    #newdata2 = [line.split('\t') for line in newdata2]

    return newdata, newdata2


def splitFileSentences3(data2, prediction):
    """이름만 이러하고, 실제 내용은 두 가지를 붙이는 것이다"""
    newdata = []
    x = prediction[0]
    x1 = prediction[1]

    for i, data_each in enumerate(data2):
        newdata.append(data_each+'\t'+str(prediction[i][0]))

    newdata = [line.split('\t') for line in newdata]

    return newdata
import importlib
rhino_spec = importlib.util.find_spec('rhinoMorph')    # 이 부분을 rhinoMorph3, rhinoMorph4 처럼 상용버전만을 위한 것으로 기록할 수 있다
found = rhino_spec is not None

if found:
    import rhinoMorph            # 이 부분을 rhinoMorph3 as rhinoMorph, rhinoMorph4 as rhinoMorph 처럼 상용버전만을 위한 것으로 기록할 수 있다
elif not found:
    rhino_spec = importlib.util.find_spec('rhinoMorph')
    found = rhino_spec is not None

    if found:
        import rhinoMorph as rhinoMorph
    else:
        print("Package Does Not Exists Error: Please install rhinoMorph (pip install rhinoMorph)")

rn = rhinoMorph.startRhino()
####################################################################################################

def listToString(s, add=''):
    '''리스트 원소를 하나의 문자열로 만듭니다'''
    str = ""
    for ele in s:
        str += ele+add
    return str


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
                                            if sample_data_appending + sample_data[idx + 1] == flat_termlist[termlistidx]:
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


def findKeySentence(data, keywords, pos='all'):
    '''입력된 keywords 원소를 하나라도 갖고 있는 data의 문장과 해당 keyword를 찾습니다'''
    #flat_termlist = makeFlatList(keywords)      # 중첩리스트를 단일리스트로 바꾼다
    flat_termlist = keywords
    print("keywords list: ", flat_termlist)

    found_sentence = []
    found_keyword = []
    for data_each in data:
        sample_data = rhinoMorph.onlyMorph_list(rn, listToString(data_each), pos=[pos])
        keyword = findKeyword(sample_data, flat_termlist)

        if len(keyword) > 0:
            found_sentence.append(listToString(data_each))
            found_keyword.append(keyword)

    result_sentences = dict(zip(found_sentence, found_keyword))     # 찾은 문장과 그 키워드를 묶는다

    return result_sentences

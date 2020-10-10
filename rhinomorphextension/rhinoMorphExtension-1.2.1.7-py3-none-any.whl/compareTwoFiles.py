def listToString(s, add=''):
    '''리스트 원소를 하나의 문자열로 만듭니다'''
    str = ""
    for ele in s:
        str += ele+add
    return str


def write_data(data, filename, encoding="cp949"):
    """쓰기 함수"""
    with open(filename, 'w', encoding=encoding) as f:
        f.write(data)


def compareFiles(file1, file2):
    onlyFile1 = []
    onlyFile2 = []

    print("File1에만 있는 라인을 추출합니다...\n")
    for file1_line in file1:
        file1_line = file1_line.strip('\n')
        found = False
        for file2_line in file2:
            file2_line = file2_line.strip('\n')
            if file1_line == file2_line:
                found = True
                break
        if not found:
            print(file1_line)
            onlyFile1.append(file1_line)

    print("***********************************")
    print("File2에만 있는 라인을 추출합니다...\n")
    for file2_line in file2:
        file2_line = file2_line.strip('\n')
        found = False
        for file1_line in file1:
            file1_line = file1_line.strip('\n')
            if file2_line == file1_line:
                found = True
                break
        if not found:
            print(file2_line)
            onlyFile2.append(file2_line)

    onlyFile1w = listToString(onlyFile1, '\n')
    onlyFile2w = listToString(onlyFile2, '\n')

    write_data(onlyFile1w, "onlyFile1.txt")
    write_data(onlyFile2w, "onlyFile2.txt")



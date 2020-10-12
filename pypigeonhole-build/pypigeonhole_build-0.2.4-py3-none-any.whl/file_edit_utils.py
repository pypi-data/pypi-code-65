import fileinput


def replace_line(file_name, what_to_find, what_to_replace):
    with fileinput.FileInput(file_name, inplace=True) as f:
        for line in f:
            if line.find(what_to_find) > -1:
                print(what_to_replace)
            else:
                print(line, end='')


def version_inc_1(version: str) -> str:
    segs = version.split('.')
    seg1 = int(segs[0])
    seg2 = int(segs[1])
    seg3 = int(segs[2])

    seg3 += 1
    if seg3 <= 9:
        return f'{seg1}.{seg2}.{seg3}'
    else:
        seg2 += 1
        seg3 -= 10

    if seg2 <= 9:
        return f'{seg1}.{seg2}.{seg3}'
    else:
        seg1 += 1
        seg2 -= 10

    return f'{seg1}.{seg2}.{seg3}'


def version_inc_2(version: str) -> str:
    segs = version.split('.')
    seg1 = int(segs[0])
    seg2 = int(segs[1])
    seg3 = int(segs[2])

    seg3 += 1
    return f'{seg1}.{seg2}.{seg3}'


def bump_version1(curr_version, file_name, line_pattern='app_version = '):
    new_ver = version_inc_1(curr_version)
    replace_line(file_name, line_pattern, 'app_version = "' + new_ver + '"')
    return new_ver


def bump_version2(curr_version, file_name, line_pattern='app_version'):
    new_ver = version_inc_2(curr_version)
    replace_line(file_name, line_pattern, 'app_version = "' + new_ver + '"')
    return new_ver

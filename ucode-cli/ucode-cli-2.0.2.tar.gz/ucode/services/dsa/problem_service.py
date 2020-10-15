import copy
import glob
import json
import os
import codecs
import re
from builtins import staticmethod
from shutil import copyfile
from typing import List, Tuple

from jinja2 import Template
from ucode.helpers.clog import CLog
from ucode.helpers.misc import make_problem_code, join_lines, make_slug
from ucode.models.problem import Problem, TestCase


def read_testcases_from_file(testcase_file):
    count = 0
    inputi = ""
    outputi = ""
    is_output = False

    testcases = []

    with open(testcase_file, 'r') as fi:
        for line in fi:
            if line.startswith("###"):

                if count > 0:
                    testcases.append({'input': inputi.strip(), 'output': outputi.strip()})

                count += 1

                is_output = False

                inputi = outputi = ""

                continue
            elif line.startswith("---"):
                is_output = True
            else:
                if is_output:
                    outputi += line
                else:
                    inputi += line
        if inputi.strip() or outputi.strip():
            testcases.append({'input': inputi.strip(), 'output': outputi.strip()})

    return testcases


def find_section(pattern, lines, start_index=0, once=False):
    indices = []
    content = {}
    for i in range(start_index, len(lines)):
        if re.match(pattern, lines[i], re.I):
            indices.append(i)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('#'):
                    break
                content.setdefault(i, [])
                content[i].append(lines[j])
            if once:
                break

    return indices, content


def fix_section_title(name, pattern, lines, replace, once=True):
    found = False
    for i in range(len(lines)):
        if re.match(pattern, lines[i], re.I):
            lines[i] = re.sub(pattern, replace, lines[i])
            CLog.info(f'AUTOFIX: Fix {name} heading style: ' + lines[i])
            found = True
            if once:
                break
    if not found:
        CLog.warn(f'AUTOFIX: {name} is probably missing, don\'t know how to fix it.')


def check_section(name, pattern, lines, proper_line, unique=True, start_index=0, log_error=True):
    lines, content = find_section(pattern, lines, start_index)
    if log_error:
        flog = CLog.error
    else:
        flog = CLog.warn
    if not lines:
        flog(f'{name} is missing or invalid: {name} should has style: `{proper_line}`')
        return None, None
    if unique and len(lines) > 1:
        CLog.error(f'Only one {name} allowed!')

    empty = True
    for isection in content:
        for line in content[isection]:
            if line.strip() and not line.startswith('[//]:'):
                empty = False
    if empty:
        flog(f'{name} is empty!')

    return lines[0], content


class ProblemService:
    @staticmethod
    def read_all_problems(base_folder, nested_folder=0,
                          load_testcase=False, translations=[]) -> List[Tuple[str, Problem]]:
        res = []
        problem_folders = [f.path for f in os.scandir(base_folder) if f.is_dir()]
        for problem_folder in sorted(problem_folders):
            if nested_folder:
                for i in range(nested_folder):
                    subfolders = [f.path for f in os.scandir(problem_folder) if f.is_dir()]
                    for folder in sorted(subfolders):
                        print(problem_folder)
                        problem = ProblemService.load_v1(os.path.join(problem_folder, folder),
                                                         load_testcase=load_testcase,
                                                         translations=translations)
                        res.append((os.path.join(problem_folder, folder), problem))
            else:
                print(problem_folder)
                problem = ProblemService.load_v1(problem_folder, load_testcase=load_testcase, translations=translations)
                res.append((problem_folder, problem))
        return res

    @staticmethod
    def check_problem_v1(problem_folder, auto_fix=False):
        problem_code, statement_file = ProblemService.detect_problem_code_in_folder(problem_folder)

        solution_file = os.path.join(problem_folder, f"{problem_code}.py")
        test_generator_file = os.path.join(problem_folder, f"{problem_code}_generator.py")
        testcase_file = os.path.join(problem_folder, f"testcases.txt")
        testcase_manual_file = os.path.join(problem_folder, f"testcases_manual.txt")

        if not os.path.isfile(solution_file):
            CLog.error(f"Solution file `{problem_code}.py` is missing!")
        if not os.path.isfile(test_generator_file):
            CLog.error(f"Testcase generator file `{problem_code}_generator.py` is missing!")
        if not os.path.isfile(testcase_file):
            CLog.error(f"Testcases file `testcases.txt` is missing!")
        else:
            file_size = os.stat(testcase_file).st_size
            if file_size > 50 * 1024 * 1024:
                CLog.error(f"Testcases file `testcases.txt` should not be > 50MB!")

        if not os.path.isfile(testcase_manual_file):
            CLog.warn(f"Manual testcases file `testcases_manual.txt` is missing!")

        with open(statement_file) as fi:
            statement = fi.read()
            # print(statement)
            lines = statement.splitlines()

            if not lines[0].startswith('[//]: # ('):
                CLog.error('The first line should be the source of the problem, ex. `[//]: # (http://source.link)`')
                if auto_fix:
                    i = 0
                    while not lines[i].strip():
                        i += 1
                    lines = lines[i:]
                    if lines[0].startswith('[//]:'):
                        lines[0] = '[//]: # (%s)' % lines[0][5:].strip()
                        CLog.info("AUTOFIX: convert source info to: " + lines[0])
                    else:
                        CLog.warn("AUTOFIX: Source info may be missed. Don't know how to fix it.")
                        lines.insert(0, '[//]: # ()')

            title_line, statement = check_section('Title', '# \S*', lines, '# Problem Title (heading 1)')
            if auto_fix and not title_line:
                heading_line, content = find_section(f'#.*{problem_code}', lines)
                proper_title = (' '.join(problem_code.split('_'))).title()
                if not heading_line:
                    CLog.info('AUTOFIX: Problem title is probably missing, adding one...')
                    title1 = f'# {proper_title}'
                    title2 = f'[//]: # ({problem_code})'
                    lines.insert(1, '')
                    lines.insert(2, title1)
                    lines.insert(3, title2)
                    print(*lines[:4], sep='\n')
                else:  # has Title but wrong format
                    lines[heading_line[0]] = f'# {proper_title}'
                    if not lines[heading_line[0] + 1].startswith("[//]:"):
                        lines.insert(heading_line[0] + 1, f'[//]: # ({problem_code})')
                    CLog.info('AUTOFIX: Fix Title style and problem code')

            if title_line:
                title = lines[title_line]
                proper_title = (' '.join(title.split('_'))).title()
                if title != proper_title:
                    CLog.warn(f'Improper title: `{title}`, should be `{proper_title}`')
                # proper_problem_code = f'[//]: # ({problem_code})'
                if not lines[title_line + 1].startswith('[//]: # ('):
                    CLog.error(f'Title should be followed by proper problem code: `problem_code`')

                if lines[title_line + 3].startswith("[//]:") and lines[0] == '[//]: # ()':
                    CLog.warn('Detect source link in statement: %s' % lines[title_line + 3])
                    if auto_fix:
                        CLog.info('AUTOFIX: Detect source link in statement: %s, moving to first line'
                                  % lines[title_line + 3])
                        lines[0] = '[//]: # (%s)' % lines[title_line + 3][5:].strip()
                        lines.pop(title_line + 3)

            input_line, input = check_section('Input', '## Input\s*$', lines, '## Input')
            if input_line and title_line and input_line < title_line:
                CLog.error('Input should go after the Problem Statement.')

            if auto_fix and input_line is None:
                fix_section_title('Input', f'(#+\s*Input|Input\s*$)', lines, f'## Input')

            constraints_line, constraints = check_section('Constraints', '## Constraints\s*$',
                                                          lines, '## Constraints')
            if constraints_line and input_line and constraints_line < input_line:
                CLog.error('Constraints should go after the Input.')

            if auto_fix and constraints_line is None:
                fix_section_title('Constraints', f'(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines,
                                  f'## Constraints')

            output_line, output = check_section('Output', '## Output\s*$', lines, '## Output')
            # if output_line and constraints_line and output_line < constraints_line:
            #     CLog.error('Output should go after the Constraints.')

            if auto_fix and output_line is None:
                fix_section_title('Output', f'(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines, f'## Output')

            tag_line, tag = check_section('Tags', '## Tags\s*$', lines, '## Tags')
            if tag_line and output_line and tag_line < output_line:
                CLog.error('Tags should go after the Output.')

            if auto_fix and tag_line is None:
                fix_section_title('Tags', f'#+\s*Tag.*', lines, f'## Tags')

            difficulty_line, difficulty = check_section('Difficulty', '## Difficulty\s*$', lines, '## Difficulty')
            if difficulty_line:
                try:
                    difficulty = float(difficulty[difficulty_line][0])
                    if difficulty < 1 or difficulty > 10:
                        CLog.error('Difficulty should be a number between 1 and 10, found: ' + str(difficulty))
                except ValueError:
                    CLog.error(
                        'Difficulty should be a number between 1 and 10, found: ' + difficulty[difficulty_line][0])

            if auto_fix and difficulty_line is None:
                fix_section_title('Difficulty', f'#+\s*Difficulty.*', lines, f'## Difficulty')

            list_lines, list_content = find_section('- .*', lines)
            for i in list_lines[::-1]:
                if i > 0:
                    prev_line = lines[i - 1]
                    if prev_line.strip() and not prev_line.startswith('- '):
                        CLog.error(f'There should be an empty line before the list, line {i}: {lines[i]}')
                        if auto_fix:
                            CLog.info('AUTOFIX: Added new line before list')
                            lines.insert(i, '')

            lines2, tmp = check_section('Sample input', '## Sample input', lines, '## Sample input 1', unique=False)
            if auto_fix and not lines2:
                fix_section_title('Sample Input', '#+\s*Sample input(.*)', lines, r'## Sample Input\1', once=False)

            lines2, tmp = check_section('Sample output', '## Sample output', lines, '## Sample output 1', unique=False)
            if auto_fix and not lines2:
                fix_section_title('Sample Output', '#+\s*Sample (ou|Ou|out|Out)put(.*)', lines, r'## Sample Output\2',
                                  once=False)

            lines2, tmp = check_section('Explanation', '## Explanation', lines, '## Explanation 1',
                                        unique=False, log_error=False)
            if auto_fix and not lines2:
                fix_section_title('Explanation', '#+\s*Explanation(.*)', lines, r'## Explanation\1', once=False)

            if auto_fix:
                statement_file_bak = os.path.join(problem_folder, f"{problem_code}_bak.md")
                i = 1
                while os.path.exists(statement_file_bak):
                    statement_file_bak = os.path.join(problem_folder, f"{problem_code}_bak{i}.md")
                    i += 1
                copyfile(statement_file, statement_file_bak)
                with open(statement_file, 'w') as f:
                    f.write('\n'.join(lines))
        return problem_code

    @staticmethod
    def detect_problem_code_in_folder(problem_folder):
        problem_code = os.path.basename(problem_folder.rstrip(os.path.sep))

        statement_file = os.path.join(problem_folder, f"{problem_code}.md")
        if not os.path.isfile(statement_file):
            statement_files = glob.glob(os.path.join(problem_folder, "*.md"))
            if len(statement_files) < 1:
                raise SyntaxError(f'Problem statement file `{problem_code}.md` is missing!')
            elif len(statement_files) == 1:
                statement_file = statement_files[0]
                problem_code = os.path.splitext(os.path.basename(statement_file))[0]
            else:
                other_files = [f for f in glob.glob(os.path.join(problem_folder, "*.md"))
                               if "_editorial.md" in f or "_tran_" in f
                               or ".vi." in f or "_bak.md" in f or "_bak1.md" in f or "_bak2.md" in f]
                if len(statement_files) - 1 != len(other_files):
                    raise SyntaxError('Problem folder contains multiple statement (.md) files, don\'t know what to do.')
                else:
                    t = set(statement_files) - set(other_files)
                    statement_file = list(t)[0]
                    problem_code = os.path.splitext(os.path.basename(statement_file))[0]
                    CLog.info(f'Auto detect problem code `{problem_code}` in  {statement_file}.md file')
        return problem_code, statement_file

    @staticmethod
    def check_problem(problem_folder):
        problem_code, statement_file = ProblemService.detect_problem_code_in_folder(problem_folder)

        tran_files = glob.glob(os.path.join(problem_folder, f"{problem_code}_tran_*.md"))
        if tran_files:
            print("Detected translation file(s):", *tran_files, sep="\n")

        stock_solution_file = os.path.join(problem_folder, f"{problem_code}.py")
        metadata_file = os.path.join(problem_folder, f"{problem_code}_meta.json")
        test_generator_file = os.path.join(problem_folder, f"{problem_code}_generator.py")
        editorial_file = os.path.join(problem_folder, f"{problem_code}_editorial.md")
        testcase_file = os.path.join(problem_folder, f"{problem_code}_testcases.txt")
        testcase_sample_file = os.path.join(problem_folder, f"{problem_code}_testcases_sample.txt")

        problem_files = {
            "statement": statement_file,
            "editorial": editorial_file,
            "metadata": metadata_file,
            "stock_solution": stock_solution_file,
            "testcases": testcase_file,
            "testcases_sample": testcase_sample_file,
            "test_generator": testcase_sample_file
        }

        if not os.path.isfile(stock_solution_file):
            CLog.error(f"Main Python solution file `{problem_code}.py` is missing!")
        if not os.path.isfile(test_generator_file):
            CLog.error(f"Testcase generator file `{problem_code}_generator.py` is missing!")
        if not os.path.isfile(metadata_file):
            CLog.error(f"Metadata file `{problem_code}_meta.json` is missing!")
        if not os.path.isfile(editorial_file):
            CLog.warn(f"Editorial file `{problem_code}_editorial.md` is missing!")
        if not os.path.isfile(testcase_file):
            CLog.error(f"Testcases file `{problem_code}_testcases.txt` is missing!")
        else:
            file_size = os.stat(testcase_file).st_size
            if file_size > 50 * 1024 * 1024:
                CLog.error(f"Testcases file `{problem_code}_testcases.txt` should not be > 50MB!")

        if not os.path.isfile(testcase_sample_file):
            CLog.warn(f"Sample testcases file `{problem_code}_testcases_sample.txt` is missing!")

        metadata = None
        with open(metadata_file) as f:
            metadata = json.load(f)

        if not metadata:
            CLog.error(f"Invalid metadata in `{problem_code}_meta.json` file")
        else:
            if not metadata.get("tags"):
                CLog.error(f"`tags` are missing in `{problem_code}_meta.json` file")
            if not metadata.get("difficulty"):
                CLog.error(f"`difficulty` is not specified in `{problem_code}_meta.json` file")
            if not metadata.get("statement_language"):
                CLog.error(f"`statement_language` is not specified in `{problem_code}_meta.json` file")

        with open(statement_file) as fi:
            statement = fi.read()
            lines = statement.splitlines()

            title_line, statement = check_section('Title', '# \S*', lines, '# Problem Title (heading 1)')

            if title_line:
                title = lines[title_line]
                proper_title = (' '.join(title.split('_'))).title()
                if title != proper_title:
                    CLog.warn(f'Improper title: `{title}`, should be `{proper_title}`')

            input_line, input = check_section('Input', '## Input\s*$', lines, '## Input')
            if input_line and title_line and input_line < title_line:
                CLog.error('Input should go after the Problem Statement.')

            constraints_line, constraints = check_section('Constraints', '## Constraints\s*$',
                                                          lines, '## Constraints')
            if constraints_line and input_line and constraints_line < input_line:
                CLog.error('Constraints should go after the Input.')

            output_line, output = check_section('Output', '## Output\s*$', lines, '## Output')
            # if output_line and constraints_line and output_line < constraints_line:
            #     CLog.error('Output should go after the Constraints.')

            if output_line is None:
                CLog.error('Missing output description')

            list_lines, list_content = find_section('- .*', lines)
            for i in list_lines[::-1]:
                if i > 0:
                    prev_line = lines[i - 1]
                    if prev_line.strip() and not prev_line.startswith('- '):
                        CLog.error(f'There should be an empty line before the list, line {i}: {lines[i]}')

            check_section('Sample input', '## Sample input', lines, '## Sample input 1', unique=False)

            check_section('Sample output', '## Sample output', lines, '## Sample output 1', unique=False)

            check_section('Explanation', '## Explanation', lines, '## Explanation 1', unique=False, log_error=False)

        return problem_code, metadata, problem_files

    @staticmethod
    def _check_folder(base_folder, problem_folder, overwrite=False):
        abs_folder = os.path.join(base_folder, problem_folder)

        if os.path.exists(abs_folder):
            if not overwrite:
                CLog.error('Problem folder existed! Delete the folder or use `overwrite` instead.')
                return None
            else:
                CLog.warn('Problem folder existed! Content will be overwritten.')

        if not os.path.exists(abs_folder):
            os.makedirs(abs_folder)

        return abs_folder

    @staticmethod
    def create_problem(folder, problem_name, problem_code=None, lang="en", translations=[], overwrite=False,
                       tags=[], difficulty=0.0):
        problem = Problem()
        problem.statement = """Nhập vào $3$ số nguyên $B$, $P$, $M$. Hãy tính:

$$R = B^P \mod M$$"""
        problem.input_format = """- Dòng đầu chứa số tự nhiên $T$ - số lượng các testcase
- $T$ dòng sau, mỗi dòng chứa $3$ số nguyên không âm $B$, $P$, $dM$."""
        problem.output_format = """$1$ số $R$ là kết quả phép tính $R = B^P \mod M$"""
        problem.constraints = """- $0 ≤ B, P ≤ 2^{31} - 1$
- $1 ≤ M ≤ 46340$"""
        problem.name = problem_name
        problem.code = problem_code
        problem.difficulty = difficulty
        problem.tags = tags
        problem.testcases_sample.append(TestCase(input="1\n2", output="3"))
        problem.testcases_sample.append(TestCase(input="4\n5", output="9"))
        if translations:
            for tran_lang in translations:
                problem.translations[tran_lang] = Problem(name=problem.name)

        ProblemService.save(problem, folder, overwrite=overwrite, lang=lang)

        CLog.important(f'Problem created at `{folder}`')

    @staticmethod
    def _parse_statement_file(statement_file, problem: Problem):
        with open(statement_file) as fi:
            statement = fi.read()
            lines = statement.splitlines()

            statement_i, statement_c = find_section('#\s+.*', lines)
            if statement_i:
                title = lines[statement_i[0]][1:].strip()
                problem.name = title

                s = lines[statement_i[0] + 1].strip()
                if not s.strip():
                    s = lines[statement_i[0] + 2]

            if statement_i:
                problem.statement = join_lines(statement_c[statement_i[0]])

            input_i, input_c = find_section('(#+\s*Input|Input\s*$)', lines)
            if input_i:
                problem.input_format = join_lines(input_c[input_i[0]])

            output_i, output_c = find_section('(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines)
            if output_i:
                problem.output_format = join_lines(output_c[output_i[0]])

            constraints_i, constraints_c = find_section('(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines)
            if constraints_i:
                problem.constraints = join_lines(constraints_c[constraints_i[0]])

            sample_input_i, sample_input_c = find_section('#+\s*Sample input(.*)', lines)
            sample_output_i, sample_output_c = find_section('#+\s*Sample (ou|Ou|out|Out)put(.*)', lines)
            explanation_i, explanation_c = find_section('#+\s*Explanation(.*)', lines)
            if sample_input_i:
                for i in range(len(sample_input_i)):
                    testcase = TestCase()
                    testcase.input = join_lines(sample_input_c[sample_input_i[i]]).strip('`').strip()
                    testcase.output = join_lines(sample_output_c[sample_output_i[i]]).strip('`').strip()
                    if len(explanation_i) > i:
                        testcase.explanation = join_lines(explanation_c[explanation_i[i]]).strip('`').strip()

                    problem.testcases.append(testcase)

    @staticmethod
    def _parse_statement_file_v1(statement_file, problem: Problem):
        with open(statement_file) as fi:
            statement = fi.read()
            lines = statement.splitlines()

            source_link = None
            s = lines[0]
            if not s.strip():
                s = lines[1]
            if s.startswith('[//]:'):
                o = s.find('(')
                if o:
                    source_link = s[o + 1:s.find(')')].strip()
                else:
                    source_link = s[5:].strip()
            problem.src_url = source_link

            statement_i, statement_c = find_section('#\s+.*', lines)
            if statement_i:
                title = lines[statement_i[0]][1:].strip()
                problem.name = title

                s = lines[statement_i[0] + 1].strip()
                if not s.strip():
                    s = lines[statement_i[0] + 2]
                if s.startswith('[//]:'):
                    problem.preview = s
                    o = s.find('(')
                    if o:
                        code = s[o + 1:s.find(')')].strip()
                    else:
                        code = s[5:].strip()
                    problem.code = code
                    problem.slug = problem.code.replace('_', '-')

            if statement_i:
                problem.statement = join_lines(statement_c[statement_i[0]])

            input_i, input_c = find_section('(#+\s*Input|Input\s*$)', lines)
            if input_i:
                problem.input_format = join_lines(input_c[input_i[0]])

            output_i, output_c = find_section('(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines)
            if output_i:
                problem.output_format = join_lines(output_c[output_i[0]])

            constraints_i, constraints_c = find_section('(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines)
            if constraints_i:
                problem.constraints = join_lines(constraints_c[constraints_i[0]])

            tags_i, tags_c = find_section('#+\s*Tag.*', lines)
            if tags_i:
                tags = []
                for t in tags_c[tags_i[0]]:
                    t = t.strip()
                    if t:
                        if t.startswith('-'):
                            tags.append(t[1:].strip())
                        else:
                            tags.append(t)
                problem.tags = problem.topics = tags

            difficulty_i, difficulty_c = find_section('#+\s*Difficulty.*', lines)
            if difficulty_i:
                try:
                    problem.difficulty = float(difficulty_c[difficulty_i[0]][0])
                except ValueError:
                    CLog.warn(f"Difficulty is not parsable: {difficulty_c[difficulty_i[0]][0]}")

            sample_input_i, sample_input_c = find_section('#+\s*Sample input(.*)', lines)
            sample_output_i, sample_output_c = find_section('#+\s*Sample (ou|Ou|out|Out)put(.*)', lines)
            explanation_i, explanation_c = find_section('#+\s*Explanation(.*)', lines)
            if sample_input_i:
                for i in range(len(sample_input_i)):
                    testcase = TestCase()
                    testcase.input = join_lines(sample_input_c[sample_input_i[i]]).strip('`').strip()
                    testcase.output = join_lines(sample_output_c[sample_output_i[i]]).strip('`').strip()
                    if len(explanation_i) > i:
                        testcase.explanation = join_lines(explanation_c[explanation_i[i]]).strip('`').strip()

                    problem.testcases.append(testcase)

    @staticmethod
    def load(problem_folder, load_testcase=False):
        problem_code, meta, problem_files = ProblemService.check_problem(problem_folder)
        print("Problem metadata:", json.dumps(meta))
        problem = Problem()
        problem.slug = make_problem_code(problem_code)
        problem.code = problem_code
        problem.preview = f'[//]: # ({problem_code})'

        if meta.get("code"):
            problem.code = meta.get("code")
        if meta.get("slug"):
            problem.slug = meta.get("slug")
        if meta.get("tags"):
            problem.tags = meta.get("tags")
        if meta.get("difficulty"):
            problem.difficulty = meta.get("difficulty")
        if meta.get("experience_gain"):
            problem.xp = meta.get("experience_gain")
        if meta.get("statement_format"):
            problem.statement_format = meta.get("statement_format")
        if meta.get("statement_language"):
            problem.statement_language = meta.get("statement_language")
        if meta.get("limit_time_ms"):
            problem.limit_time = meta.get("limit_time_ms")
        if meta.get("limit_memory_mb"):
            problem.limit_memory = meta.get("limit_memory_mb")
        if meta.get("testcase_format"):
            problem.testcase_format = meta.get("testcase_format")
        if meta.get("src_name"):
            problem.src_name = meta.get("src_name")
        if meta.get("src_id"):
            problem.src_id = meta.get("src_id")
        if meta.get("src_url"):
            problem.src_url = meta.get("src_url")

        print("src", problem.src_url)

        if os.path.exists(problem_files["editorial"]):
            editorial_prob = Problem()
            ProblemService._parse_statement_file(problem_files["editorial"], editorial_prob)
            if editorial_prob.statement.strip():
                problem.editorial = editorial_prob.statement
            else:
                with open(problem_files["editorial"]) as fi:
                    problem.editorial = fi.read()

        ProblemService._parse_statement_file(problem_files["statement"], problem)
        if meta.get("statement_translations"):
            for lang in meta["statement_translations"]:
                lang_statement_file = os.path.join(problem_folder, f"{problem_code}_tran_{lang}.md")
                if not os.path.exists(lang_statement_file):
                    CLog.warn(f"Translation file not existed: {lang_statement_file}")
                else:
                    tran_problem = copy.copy(problem)
                    ProblemService._parse_statement_file(lang_statement_file, tran_problem)
                    problem.translations[lang] = tran_problem

        solution_file = os.path.join(problem_folder, f"{problem_code}.py")
        if os.path.isfile(solution_file):
            with open(solution_file) as f:
                problem.solution = f.read()

        additional_solution_files = glob.glob(os.path.join(problem_folder, f"{problem_code}_solution.*"))
        for file_path in additional_solution_files:
            sub_path = os.path.join(problem_folder, f"{problem_code}_solution")
            idx = file_path.find(sub_path) + len(sub_path)
            with open(file_path) as f:
                problem.solutions.append({"lang": file_path[idx + 1:],
                                          "code": f.read()})
        # print(*problem.solutions, sep="\n")

        testcase_generators = glob.glob(os.path.join(problem_folder, f"{problem_code}_generator.*"))
        if testcase_generators:
            file_path = testcase_generators[0]
            if os.path.exists(file_path):
                idx = file_path.rfind(".")
                with open(file_path) as f:
                    problem.testcase_generator = {"lang": file_path[idx + 1:], "code": f.read()}
            # print(problem.testcase_generator)

        problem.testcases = []
        if load_testcase:
            file_names = ["testcases_sample_stock.txt", "testcases_sample.txt", "testcases_stock.txt", "testcases.txt"]
            input_set = set()
            for file_name in file_names:
                testcase_file = os.path.abspath(os.path.join(problem_folder, f"{problem_code}_{file_name}"))

                if not os.path.exists(testcase_file):
                    CLog.info(f'`{testcase_file}` file not existed, skipping...')
                else:
                    tests = read_testcases_from_file(testcase_file)
                    # print(f"reading testcases in file {testcase_file}: {len(tests)}")
                    for t in tests:
                        _input, _output = t['input'], t['output']
                        # print(f"Input: {input}, output: {output}")
                        if _input not in input_set:
                            problem.testcases.append(TestCase(input=_input, output=_output))
                        if "_sample" in file_name:
                            problem.testcases_sample.append(TestCase(input=_input, output=_output))
                        input_set.add(_input)
                        # print(input_set)
            print(f"Loaded {len(problem.testcases)} testcases")

        if not problem.testcases_sample and problem.testcases:
            problem.testcases_sample = problem.testcases[:2]

        return problem

    @staticmethod
    def load_v1(problem_folder, load_testcase=False, translations=[]):
        """

        :param problem_folder:
        :param load_testcase:
        :param translations: ['vi']
        :return:
        """
        problem_code = ProblemService.check_problem_v1(problem_folder)
        statement_file = os.path.join(problem_folder, f"{problem_code}.md")
        editorial_file = os.path.join(problem_folder, f"{problem_code}_editorial.md")

        problem = Problem()
        problem.slug = make_problem_code(problem_code)
        problem.code = problem_code
        problem.preview = f'[//]: # ({problem_code})'

        if os.path.exists(editorial_file):
            editorial_prob = Problem()
            ProblemService._parse_statement_file_v1(editorial_file, editorial_prob)
            if editorial_prob.statement.strip():
                problem.editorial = editorial_prob.statement
            else:
                with open(editorial_file) as fi:
                    problem.editorial = fi.read()

        ProblemService._parse_statement_file_v1(statement_file, problem)
        if translations:
            for lang in translations:
                lang_statement_file = os.path.join(problem_folder, f"{problem_code}.{lang}.md")
                if not os.path.exists(lang_statement_file):
                    CLog.warn(f"Translation file not existed: {lang_statement_file}")
                else:
                    tran_problem = copy.copy(problem)
                    ProblemService._parse_statement_file_v1(lang_statement_file, tran_problem)
                    problem.translations[lang] = tran_problem

        solution_file = os.path.join(problem_folder, f"{problem_code}.py")
        if os.path.isfile(solution_file):
            with open(solution_file) as f:
                problem.solution = f.read()

        additional_solution_files = glob.glob(os.path.join(problem_folder, f"solution.*"))
        for file_path in additional_solution_files:
            sub_path = os.path.join(problem_folder, "solution")
            idx = file_path.find(sub_path) + len(sub_path)
            with open(file_path) as f:
                problem.solutions.append({"lang": file_path[idx + 1:],
                                          "code": f.read()})
        # print(*problem.solutions, sep="\n")

        testcase_generators = glob.glob(os.path.join(problem_folder, f"{problem_code}_generator.*"))
        if testcase_generators:
            file_path = testcase_generators[0]
            if os.path.exists(file_path):
                idx = file_path.rfind(".")
                with open(file_path) as f:
                    problem.testcase_generator = {"lang": file_path[idx + 1:], "code": f.read()}
            # print(problem.testcase_generator)

        problem.testcases = []
        if load_testcase:
            file_names = ["testcases_manual_stock.txt", "testcases_manual.txt", "testcases_stock.txt", "testcases.txt"]
            input_set = set()
            for file_name in file_names:
                testcase_file = os.path.abspath(os.path.join(problem_folder, file_name))

                if not os.path.exists(testcase_file):
                    CLog.warn(f'`{testcase_file}` file not existed, skipping...')
                else:
                    tests = read_testcases_from_file(testcase_file)
                    # print(f"reading testcases in file {testcase_file}: {len(tests)}")
                    for t in tests:
                        _input, _output = t['input'], t['output']
                        # print(f"Input: {input}, output: {output}")
                        if _input not in input_set:
                            problem.testcases.append(TestCase(input=_input, output=_output))
                        if "manual_stock" in file_name:
                            problem.testcases_sample.append(TestCase(input=_input, output=_output))
                        input_set.add(_input)
                        # print(input_set)
            print(f"Loaded {len(problem.testcases)} testcases")

        if not problem.testcases_sample and problem.testcases:
            problem.testcases_sample = problem.testcases[:2]

        return problem

    @staticmethod
    def save(problem : Problem, base_folder=".", problem_folder=None, problem_code=None, overwrite=False, lang=None):
        """
        :param problem:
        :param problem_code: name of problem folder
        :param base_folder: the parent folder that will contain the problem folder
        :return:
        """
        if not problem_code:
            problem_code = problem.name

        problem_code = make_problem_code(problem_code)

        problem.code = problem_code
        if not problem_folder:
            problem_folder = problem_code
        problem_folder = ProblemService._check_folder(base_folder, problem_folder, overwrite)
        if not problem_folder:
            return

        if not problem.name:
            problem.name = (' '.join(problem_code.split('_'))).title()

        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

        testcases = []
        if problem.stock_testcases:
            testcases += problem.stock_testcases
        if problem.testcases:
            testcases += problem.testcases

        with open(os.path.join(template_path, 'testcases.txt.j2')) as file_:
            template = Template(file_.read())
            content = template.render(testcases=testcases)
            f = open(problem_folder + f"/{problem_code}_testcases.txt", 'w')
            f.write(content)
            f.close()

        sample_testcases = []
        if problem.testcases_sample:
            sample_testcases += problem.testcases_sample
        if problem.stock_testcases_sample:
            sample_testcases += problem.stock_testcases_sample

        with open(os.path.join(template_path, 'testcases.txt.j2')) as file_:
            template = Template(file_.read())
            content = template.render(testcases=problem.testcases_sample)
            f = open(problem_folder + f"/{problem_code}_testcases_sample.txt", 'w')
            f.write(content)
            f.close()

        problem.testcases_sample = sample_testcases

        if lang:
            problem.statement_language = lang
        print("src", problem.src_url)

        with open(os.path.join(template_path, 'meta.json.j2')) as file_:
            template = Template(file_.read())
            meta = template.render(problem=problem,
                                   statement_translations=json.dumps(list(problem.translations.keys())),
                                   tags=json.dumps(problem.tags))
            f = codecs.open(problem_folder + ("/%s_meta.json" % problem_code), "w", "utf-8")
            f.write(meta)
            f.close()

        with open(os.path.join(template_path, 'statement.md.j2')) as file_:
            template = Template(file_.read())
            statement = template.render(problem=problem)
            f = codecs.open(problem_folder + ("/%s.md" % problem_code), "w", "utf-8")
            f.write(statement)
            f.close()

        for lang, prob_tran in problem.translations.items():
            with open(os.path.join(template_path, 'statement.md.j2')) as file_:
                template = Template(file_.read())
                statement = template.render(problem=prob_tran)
                f = codecs.open(problem_folder + (f"/{problem_code}_tran_{lang}.md"), "w", "utf-8")
                f.write(statement)
                f.close()

        with open(os.path.join(template_path, 'editorial.md.j2')) as file_:
            template = Template(file_.read())
            if not problem.editorial:
                problem.editorial = ""
            statement = template.render(problem=problem)
            f = codecs.open(problem_folder + ("/%s_editorial.md" % problem_code), "w", "utf-8")
            f.write(statement)
            f.close()

        if not problem.solution:
            with open(os.path.join(template_path, 'solution.py.j2')) as file_:
                template = Template(file_.read())
                content = template.render(problem_code=problem_code,
                                          solution=problem.solution if problem.solution else "pass")
                f = open(problem_folder + (f"/{problem_code}.py"), 'w')
                f.write(content)
                f.close()
        else:
            f = open(problem_folder + (f"/{problem_code}.py"), 'w')
            f.write(problem.solution)
            f.close()

        if not problem.testcase_generator:
            with open(os.path.join(template_path, 'generator.py.j2')) as file_:
                template = Template(file_.read())
                content = template.render(problem_code=problem_code)
                f = open(problem_folder + (f"/{problem_code}_generator.py"), 'w')
                f.write(content)
                f.close()
        else:
            f = open(f"{problem_folder}/{problem_code}_generator.{problem.testcase_generator['lang']}", 'w')
            f.write(problem.testcase_generator["code"])
            f.close()

        if problem.solutions:
            for solution in problem.solutions:
                f = open(f"{problem_folder}/{problem_code}_solution.{solution['lang']}", 'w')
                f.write(solution["code"])
                f.close()

        problem_folder = os.path.abspath(problem_folder)

        CLog.important(f'Problem created at `{problem_folder}`')


if __name__ == "__main__":
    # DsaProblem.create_problem('../../problems', 'Counting Sort 3', lang="en",
    #                           translations=['vi', 'ru'],
    #                           overwrite=True,
    #                           tags=['math', '800'],
    #                           difficulty=2.5)

    # problem = DsaProblem.load_v1('/home/thuc/projects/ucode/weekly-algorithm-problems/week03/p01_elephant',
    #                       translations=['vi'], load_testcase=True)
    # problem = DsaProblem.load_v1('/home/thuc/projects/ucode/weekly-algorithm-problems/week03/p02_key_races',
    #                       translations=['vi'], load_testcase=True)
    problem = ProblemService.load('/home/thuc/projects/ucode/ucode-cli/ucode/problems/p02_key_races', load_testcase=True)
    print(problem.name)
    # print(problem.translations['vi'].statement)
    # print(problem.editorial)
    # DsaProblem.save(problem, "../../problems", overwrite=True, problem_folder="p02_key_races")
    ProblemService.save(problem, "../../problems", overwrite=True)

    # load_problem('/home/thuc/teko/online-judge/dsa-problems/number_theory/num001_sumab')
    # load_problem('/home/thuc/teko/online-judge/dsa-problems/unsorted/minhhhh/m010_odd_to_even')
    # problem = load_problem('/home/thuc/teko/online-judge/ptoolbox/problems/array001_counting_sort3')
    # dsa_problem = DsaProblem.load('/home/thuc/teko/online-judge/dsa-problems/number_theory/num001_sumab')
    # print(dsa_problem.prints())




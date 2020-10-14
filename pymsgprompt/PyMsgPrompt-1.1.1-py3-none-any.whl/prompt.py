import sys
import re
import time
import _io
import platform

from pymsgprompt.handler import default_on_error, default_on_success



if 'WINDOWS' in platform.platform().upper(): 
    __universal_newline__ = '\r\n'
elif 'LINUX' in platform.platform().upper() or 'UNIX' in platform.platform().upper():
    __universal_newline__ = '\n'
elif platform.mac_ver()[0].strip() == '':
    if int(platform.mac_ver()[0].strip().split()[0]) > 9:
        __universal_newline__ = '\n'
    else:
        __universal_newline__ = '\r'
else:
    __universal_newline__ = '\n'

__prev_print_len__ = 0 # Don't modify this line


def log(message, logtype='info', end=__universal_newline__, file=None, timestamp=True, reset=False):
    global __prev_print_len__
    if not isinstance(message, str):
        raise TypeError('positional argument `message` must be a str object, but got %s'%(type(message).__name__), )

    if not isinstance(logtype, str):
        raise TypeError('postional argument `logtype` must be a str object, but got %s'%(type(logtype).__name__, ))
    
    logtype = logtype.lower().strip()
    if logtype not in('info', 'warn', 'error'):
        raise ValueError('positional argument logtype must be among `info` or `err` or `error`.')

    if end is not None and not isinstance(end, str):
        raise TypeError('positional argument `end` must be either None or a str object, but got %s'%(type(end).__name__, ))
    
    if file is not None and not isinstance(file, _io.TextIOWrapper):
        raise TypeError('positional argument `file` must be either None or a _io.TextIOWrapper object, but got %s'%(type(file).__name__), ) 

    if not isinstance(timestamp, bool):
        raise TypeError('postional argument `timestamp` must be a bool object, but got %s'%(type(timestamp).__name__, ))

    if end is None:
        sameline = True
        end = '\r'
        if file is not None:
            raise ValueError('positional argument `file` must be `None` when `end` is `None`.')
    else:
        sameline = False
    if file is None:
        file = sys.stderr if logtype in ('error', 'warn') else sys.stdout
    else:
        if file.writable():
            if 'b' in file.mode:
                raise ValueError('positional argument `file` should be opened in `write string` mode only')
        else:
            raise ValueError('positional argument `file` must be opened in `write string` mode only')

    if timestamp:
        msg_prefix = '[%s] %s: '%(logtype.upper(), time.strftime(r'%Y-%b-%d %H:%M:%S', time.localtime()))
    else:
        msg_prefix = ''
    message = '%s%s'%(msg_prefix, message)
    __this_print_len__ = len(message)
    if __prev_print_len__ > __this_print_len__:
        message += ' '*(__prev_print_len__ - __this_print_len__)
    message += end
    file.write(message)
    if sameline:
        file.flush()
    __prev_print_len__ = __this_print_len__
    if reset:
        __prev_print_len__ = 0
    return __this_print_len__


def ask(question,
            choices=None, default=None, timestamp=True,
            regexp=False, ignore_case=True,
            on_error=default_on_error, on_success=default_on_success):
    if not isinstance(regexp, bool):
        raise TypeError('postional argument `regexp` must be a bool object, but got %s'%(type(timestamp).__name__, ))

    if not isinstance(timestamp, bool):
        raise TypeError('postional argument `timestamp` must be a bool object, but got %s'%(type(timestamp).__name__, ))
    
    if not isinstance(question, str):
        raise TypeError('positional argument `question` must be a str object, but got %s'%(type(question).__name__), )
    question = question.strip()
    if not question.endswith('?'):
        question += '?'
    if choices is not None:
        if not isinstance(choices, (tuple, list)):
            raise TypeError('positional argument `choices` must be either either list, tuple type or a NoneType object, but got %s'%(
                type(choices).__name__),
            )
        choices = list(set([str(choice).strip() for choice in choices]))
        if len(choices) < 2:
            raise ValueError('positional argument `choices` must have atleast 2 choices')
        question += ' (%s)'%('/ '.join(choices), )
        

    if default is not None:
        if not isinstance(default, str):
            raise TypeError('positional argument `default` must be a str object, but got %s'%(type(default).__name__, ))
        default = default.strip()

        if choices is not None:
            invalid_default = True
            for choice in choices:
                if ignore_case:
                    if choice.upper() == default.upper():
                        invalid_default = False
                        break
                else:
                    if choice == default:
                        invalid_default = False
                        break
            if invalid_default:
                raise ValueError('positional argument `default` is having an invalid value %s'%(default, ))

        question += '[%s]'%(default, )
    
    if timestamp:
        question = '[QUES] %s: %s'%(time.strftime(r'%Y-%b-%d %H:%M:%S', time.localtime()), question)
    answer = None
    if sys.version_info[0] == 2:
        answer = raw_input(question).strip()
    elif sys.version_info[1] >= 3:
        answer = input(question).strip()
    else:
        raise EnvironmentError('This python version %s is not supported.'%('.'.join(list(sys.version_info))))
    if answer == '':
        if default is not None:
            answer = default
        elif choices is not None:
            answer=choices[0]
        else:
            on_success(question, answer)
    if choices is not None:
        answers = []
        invalid_answer = True
        if regexp:
            answer_ = '^'
            for char in answer:
                if re.match('^[a-z0-9_]$', char, flags=re.IGNORECASE) is not None:
                    answer_ += char
                else:
                    answer_ += '\\%s'%(char, )
            for choice in choices:
                if ignore_case:
                    if re.match(answer_, choice, flags=re.IGNORECASE) is not None:
                        invalid_answer = False
                        answers.append(choice)
                else:
                    if re.match(answer_, choice) is not None:
                        invalid_answer = False
                        answers.append(choice)
        else:
            for choice in choices:
                if ignore_case:
                    if choice.upper().startswith(answer.upper()):
                        answers.append(choice)
                        invalid_answer = False
                else:
                    if choice.startswith(answer):
                        answers.append(choice)
                        invalid_answer = False
        
        if invalid_answer:
            on_error(question, choices, default, 'Invalid answer by the user')
        else:
            if len(answers) > 1:
                answer_found = False
                for choice in choices:
                    if answer.upper() == choice.upper():
                        answer_found = True
                        on_success(question, choice)
                        break
                if not answer_found:
                    on_error(question, choices, default, 'Multiple answers have been matched')
            else:
                on_success(question, answers[0])
    return answer
    

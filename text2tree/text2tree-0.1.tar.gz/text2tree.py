# -*- coding: utf-8 -*-
import os.path as osp, re
import logging, subprocess, os, glob, shutil

DEFAULT_LOGGING_LEVEL = logging.INFO
def setup_logger(name='text2tree'):
    if name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.info('Logger %s is already defined', name)
    else:
        fmt = logging.Formatter(
            fmt = (
                '\033[33m%(levelname)7s:%(asctime)s:%(module)s:%(lineno)s\033[0m'
                + ' %(message)s'
                ),
            datefmt='%Y-%m-%d %H:%M:%S'
            )
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        logger = logging.getLogger(name)
        logger.setLevel(DEFAULT_LOGGING_LEVEL)
        logger.addHandler(handler)
    return logger
logger = setup_logger()

def debug(flag=True):
    """Sets the logger level to debug (for True) or warning (for False)"""
    logger.setLevel(logging.DEBUG if flag else DEFAULT_LOGGING_LEVEL)

def is_string(string):
    """
    Checks strictly whether `string` is a string
    Python 2/3 compatibility (https://stackoverflow.com/a/22679982/9209944)
    """
    try:
        basestring
    except NameError:
        basestring = str
    return isinstance(string, basestring)




class IntPointer(object):
    """
    Object that contains an integer that can be moved around
    """
    def __init__(self, value=0):
        self.value = value

    def __repr__(self):
        return '(*){}'.format(self.value)

    def __add__(self, o):
        self.value += o
        return self

class StringPointer(object):
    """
    Object that contains an string that can be moved around
    """
    def __init__(self, value=''):
        self.value = value

    def __repr__(self):
        return '(*){}'.format(self.value)

    def __add__(self, o):
        self.value += o
        return self

# ____________________
# Base blocks for any language

class BaseBlock(object):
    """
    Abstract base class for any further building blocks
    """
    forbid_new_openings = False
    closeable_by_eof = True
    close_immediately = False
    n_look_ahead = 100

    def __init__(self, *args, **kwargs):
        super(BaseBlock, self).__init__()
        self.children = []
        self.parent = None
        self.subtree = None
        self.i_open = 0
        self.i_close = 0
        self.is_closed = False

    def closeable(self, text, i):
        return False

    @classmethod
    def openable(cls, text, i):
        return False

    def advance_at_close(self):
        return 0

    def advance_at_open(self):
        return 0

    def execute_at_open(self, text, i, source_path=None):
        pass

    def execute_at_close(self, text, i, source_path=None):
        pass

    def preparse(self):
        return ''

    def postparse(self):
        return ''

    def parse(self, s=None, only_children=False, expand_subtrees=True):
        """
        Recursively parses the interpreted text back starting from this node.
        If only_children is True, only the children will be parsed and this node's
        own preparse and postparse methods will be skipped.
        """
        if s is None: s = StringPointer()
        if self.subtree and expand_subtrees:
            self.subtree.parse(s, only_children, expand_subtrees)
        else:
            if not(only_children): s += self.preparse()
            for c in self.children:
                c.parse(s=s)
            if not(only_children): s += self.postparse()
        return s.value

    def traverse(self, *args, **kwargs):
        """
        Just a wrapper for traverse(self)
        """
        for node in traverse(self, *args, **kwargs):
            yield node


class RootBlock(BaseBlock):
    """
    Starting node for any tree
    """
    def __init__(self):
        super(RootBlock, self).__init__()

class PlainBlock(BaseBlock):
    """
    Block to store plain text in, if the text does not belong to any other block
    """
    def __init__(self):
        super(PlainBlock, self).__init__()
        self.text = ''

    def __repr__(self):
        text = self.text[:10] + '...' if len(self.text)>13 else self.text[:13]
        return super(PlainBlock, self).__repr__().replace('object', 'object {}'.format(repr(text)))

    def preparse(self):
        return self.text

class OpenAndCloseTagsBlock(BaseBlock):
    """
    Base block for tags that are defined with an open tag and close tag
    """
    open_tag = '('
    close_tag = ')'
    escape_seq = None
    closeable_by_eof = False

    def __init__(self, *args, **kwargs):
        super(OpenAndCloseTagsBlock, self).__init__(*args, **kwargs)

    def closeable(self, text, i):
        return self.check_escape_seq(text, i) and self.close_tag == text[i.value:i.value+len(self.close_tag)]

    @classmethod
    def check_escape_seq(cls, text, i):
        """
        Checks if the open_tag is not immediately preceded by an escape sequence
        """
        if not(cls.escape_seq): return True # Nothing to escape
        return text[i.value-len(cls.escape_seq):i.value] != cls.escape_seq

    @classmethod
    def openable(cls, text, i):
        return cls.check_escape_seq(text, i) and cls.open_tag == text[i.value:i.value+len(cls.open_tag)]

    def __repr__(self):
        return super().__repr__().replace('object', 'object \'{}\''.format(self.open_tag))

    def advance_at_close(self):
        return len(self.close_tag)

    def advance_at_open(self):
        return len(self.open_tag)

    def preparse(self):
        return self.open_tag

    def postparse(self):
        return self.close_tag

# ____________________
# Toy language

class ToyFunctionBlock(OpenAndCloseTagsBlock):
    open_tag = 'function('
    close_tag = ')'

class ToyBracketBlock(OpenAndCloseTagsBlock):
    open_tag = '('
    close_tag = ')'

ToyLanguage = [
    ToyFunctionBlock,
    ToyBracketBlock
    ]

# ____________________
# Latex

class LatexBackslashBlock(BaseBlock):
    """
    The backslash functions as an escape char too
    """
    close_immediately = True

    @classmethod
    def openable(cls, text, i):
        if i.value+1 == len(text): return False # Can't look ahead if the \ is the final char in the text
        return (
            text[i.value] == '\\' and text[i.value-1] != '\\'
            and text[i.value+1] in ['&', '%', '$', '#', '_', '{', '}', '~', '^', '\\']
            )

    def __init__(self, text, i):
        super(LatexBackslashBlock, self).__init__()
        self.text = text[i.value:i.value+2]

    def __repr__(self):
        return super(LatexBackslashBlock, self).__repr__().replace('object', 'object {}'.format(repr(self.text)))

    def advance_at_open(self):
        return 2

    def preparse(self):
        return self.text

class LatexBracketBlock(OpenAndCloseTagsBlock):
    open_tag = '{'
    close_tag = '}'

    @classmethod
    def openable(cls, text, i):
        return cls.open_tag == text[i.value] and text[i.value-1] != '\\'

class LatexCommentBlock(OpenAndCloseTagsBlock):
    open_tag = '%'
    close_tag = '\n'
    closeable_by_eof = True
    forbid_new_openings = True
    _LATEX_NOCOMMENTS = False

    def parse(self, *args, **kwargs):
        if self._LATEX_NOCOMMENTS: return ''
        return super(LatexCommentBlock, self).parse(*args, **kwargs)

class LatexCommandBlock(OpenAndCloseTagsBlock):
    close_tag = '}'
    open_pat = re.compile(r'\\(\w+){')
    open_pat_with_brackets = re.compile(r'\\(\w+)\[[^\n]*\]{')
    _LAST_MATCH = None

    def __init__(self, *args, **kwargs):
        super(LatexCommandBlock, self).__init__(*args, **kwargs)
        text, i = args
        self.open_tag = self._LAST_MATCH.group()
        self.command = self._LAST_MATCH.group(1)

    @classmethod
    def openable(cls, text, i):
        match = cls.open_pat.match(text[i.value:i.value+cls.n_look_ahead])
        if not match:
            match = cls.open_pat_with_brackets.match(text[i.value:i.value+cls.n_look_ahead])
        if match:
            # Hack: save the match in class variable so it doesn't have to be evaluated again
            # Only works if object will be opened immediately after
            cls._LAST_MATCH = match
            return True
        return False

    def execute_at_close(self, text, i, source_path):
        if self.command == 'input':
            if source_path is None:
                logger.warning('Could not expand %s; no source_path given', self)
                return
            filename = parse_latex_nocomments(self, only_children=True).strip()
            if not filename.endswith('.tex'): filename += '.tex'
            for path in source_path:
                full_path = osp.abspath(osp.join(path, filename))
                if osp.isfile(full_path):
                    break
            else:
                logger.warning('Could not expand file \'%s\'; not on the path (%s)', filename, ', '.join(source_path))
                return
            # Read the imported file
            logger.info('Reading inputted file %s', full_path)
            with open(full_path, 'r') as f:
                subtext = f.read()
                self.subtree = interpret(subtext, language='latex', source_path=source_path)

class LatexBeginBlock(OpenAndCloseTagsBlock):
    open_pat = re.compile(r'\\begin{(\w+)}')

    def __init__(self, *args, **kwargs):
        super(LatexBeginBlock, self).__init__(*args, **kwargs)
        text, i = args
        match = self.open_pat.match(text[i.value:i.value+self.n_look_ahead])
        self.open_tag = match.group()
        self.close_tag = self.open_tag.replace('begin', 'end', 1)
        self.env_name = match.group(1)
        if self.env_name in [ 'verbatim', 'lstlisting' ]: self.forbid_new_openings = True

    @classmethod
    def openable(cls, text, i):
        return cls.open_pat.match(text[i.value:i.value+cls.n_look_ahead])

LatexLanguage = [
    LatexBackslashBlock,
    LatexCommentBlock,
    LatexBeginBlock,
    LatexCommandBlock,
    LatexBracketBlock
    ]

def parse_latex_nocomments(node, *args, **kwargs):
    """
    Parse function for latex to ignore comments
    """
    current_state = LatexCommentBlock._LATEX_NOCOMMENTS
    LatexCommentBlock._LATEX_NOCOMMENTS = True
    s = parse(node, *args, **kwargs)
    LatexCommentBlock._LATEX_NOCOMMENTS = current_state
    return s

# ____________________
# interpret

LANGUAGES = {
    'toy' : ToyLanguage,
    'latex' : LatexLanguage,
    }

def traverse(node, depth=0, **kwargs):
    """
    Traverses starting from `node` in dfs_preorder
    """
    return_depth = kwargs.get('return_depth', False)
    if isinstance(node, RootBlock) and kwargs.get('skip_root', False):
        # Don't yield the node if it's RootBlock and skip_root was True
        pass
    else:
        # If expand_subtrees is True (default), yield subtree instead of the node itself
        if node.subtree and kwargs.get('expand_subtrees', True):
            kwargs.pop('skip_root', None)
            for c in traverse(node.subtree, depth=depth, skip_root=True, **kwargs):
                yield c
        else:
            yield (node, depth) if return_depth else node
    # Recurse over the children
    for child in node.children:
        for c in traverse(child, depth=depth+1, **kwargs):
            yield c

def print_tree(node, **kwargs):
    for node, depth in traverse(node, return_depth=True, **kwargs):
        print('  '*depth + repr(node))


# def parse(node, s=None, only_children=False, expand_subtrees=True):
#     """
#     Recursively parses the interpreted text back starting from node.
#     If only_children is True, only the children will be parsed and node's
#     own preparse and postparse methods will be skipped.
#     """
#     if s is None: s = StringPointer()
#     if node.subtree and expand_subtrees:
#         node.subtree.parse(s, only_children, expand_subtrees)
#     else:
#         if not(only_children): s += node.preparse()
#         for c in node.children:
#             c.parse(s=s)
#         if not(only_children): s += node.postparse()
#     return s.value

def parse(node, *args, **kwargs):
    return node.parse(*args, **kwargs)

def interpret(
    text, language,
    source_path=None
    ):
    if is_string(language): language = LANGUAGES[language]
    if is_string(source_path): source_path = [source_path]

    reached_eof = False
    i = IntPointer(0)

    root_block = RootBlock()
    parent_block = None
    active_block = root_block
    plain_block = PlainBlock()

    while not reached_eof:
        logger.debug(
            'Iteration i=%s, active_block=%s, parent_block=%s, plain_block.text=%s',
            i.value, active_block, parent_block, repr(plain_block.text)
            )
        if i.value >= len(text):
            reached_eof = True
            logger.debug('Reached EOF at i=%s', i.value)
            break

        # The current index closes the active block
        if active_block and active_block.closeable(text, i):
            logger.debug('Closing block %s at %s', active_block, i.value)
            active_block.is_closed = True
            active_block.i_close = i.value
            i += active_block.advance_at_close()
            # If some text is in the buffer, add it to the active block and reset it
            if plain_block.text:
                active_block.children.append(plain_block)
                plain_block = PlainBlock()
            active_block.execute_at_close(text, i, source_path)
            # return to the parent scope
            active_block = parent_block
            parent_block = parent_block.parent
            continue

        # The current index opens a new active block
        forbid_new_openings = active_block.forbid_new_openings if active_block else False
        if not(forbid_new_openings):
            do_continue = False
            for Block in language:
                if Block.openable(text, i):
                    # If some text is in the buffer, add it to the active block and reset it
                    if plain_block.text:
                        active_block.children.append(plain_block)
                        plain_block = PlainBlock()
                    new_block = Block(text, i)
                    logger.debug('Opening new block %s at %s', new_block, i.value)
                    new_block.parent = active_block
                    active_block.children.append(new_block)
                    new_block.i_open = i.value
                    i += new_block.advance_at_open()
                    new_block.execute_at_open(text, i, source_path)
                    # Set scope to the newly created block, unless it closes immediately
                    if not new_block.close_immediately:
                        parent_block = active_block
                        active_block = new_block
                    do_continue = True
                    break
            if do_continue: continue

        # No active block is closed and no new block is opened;
        # push the character to a PlainBlock and advance index by 1
        plain_block.text += text[i.value]
        i += 1

    # Push any remaining text to the final active node (typically the root)
    if plain_block.text:
        active_block.children.append(plain_block)

    # Check for any remaining open blocks
    for block in traverse(root_block):
        if not(block.is_closed):
            if block.closeable_by_eof:
                # Set the index to simply the last index
                block.i_close = i.value
            else:
                raise Exception(
                    'Expected block {} to be closed, but reached EOF'
                    .format(block)
                    )

    return root_block

def interpret_file(filename, *args, **kwargs):
    """
    Wrapper around `interpret` which takes a file instead of a string
    """
    with open(filename, 'r') as f:
        text = f.read()
    # Add the dirname of the filename to the source_path
    source_path = kwargs.pop('source_path', [])
    if is_string(source_path): source_path = [source_path]
    source_path.append(osp.dirname(osp.abspath(filename)))
    kwargs['source_path'] = source_path
    return interpret(text, *args, **kwargs)

#######
# title: pytex.py
#
# language: python3
# author: bue
# date: 2020-04-00
# license: GPL>=v3
#
# description:
#     functions generate tex syntax for result reporting
######


# library
import datetime
import os


# functions

############################
#### begin documenclass ####
############################

def documentclass_article(
        s_title,
        s_author = 'Elmar Bucher',
        s_date = '{}'.format(datetime.datetime.today().isoformat(' ')),
        s_geometry = None,
        es_usepackage = {'graphicx','hyperref'},   # 'enumitem'
        b_caption_left = False,
    ):
    '''
    input:
        s_title: document title string
        s_author: author name string. evt combined with date and time.
        es_usepackage: latex libraries that schould be loaded.
        b_caption_left: should all caption be left aligned instead of the
            default centered alignement?

    output:
        ls_tex: latex code, stored as list of strings.

    description:
        generate code for the latex article class.
        outputs the code as list of strings.
    '''
    # generate tex
    ls_tex = []
    ls_tex.append(r'\documentclass{article}')
    if not (s_geometry is None):
        ls_tex.append(r'\usepackage[{}]{{geometry}}'.format(s_geometry))
    for s_usepackage in sorted(es_usepackage):
        ls_tex.append(r'\usepackage{{{}}}'.format(s_usepackage))
    if (b_caption_left):
        ls_tex.append(r'\usepackage{caption}')
        ls_tex.append(r'\captionsetup{justification=raggedright, singlelinecheck=false}')
    ls_tex.append(r'')
    ls_tex.append(r'\title{{{}}}'.format(s_title))
    if not (s_author is None):
        ls_tex.append(r'\author{{{}}}'.format(s_author))
    if not (s_date is None):
        ls_tex.append(r'\date{{{}}}'.format(s_date))
    ls_tex.append(r'')
    ls_tex.append(r'')
    ls_tex.append(r'% begin document')
    ls_tex.append(r'\begin{document}')
    ls_tex.append(r'\maketitle')
    ls_tex.append(r'')

    # output
    return(ls_tex)


def documentclass_proc(
        s_title,
        s_author = 'Elmar Bucher {}'.format(datetime.date.today().isoformat()), #format(datetime.datetime.today().isoformat(' ')),
        es_usepackage = {'graphicx','hyperref','caption'},  # 'enumitem'
        b_caption_left = False,
    ):
    '''
    input:
        s_title: document title string
        s_author: author name string. evt combined with date and time.
        es_usepackage: latex libraries that schould be loaded.
        b_caption_left: should all caption be left aligned instead of the
            default centered alignement?

    output:
        ls_tex: latex code, stored as list of strings.

    description:
        generate code for the latex proceedings class, which has column of text.
        outputs the code as list of strings.
    '''
    # generate tex
    ls_tex = []
    ls_tex.append(r'\documentclass{proc}')
    for s_usepackage in sorted(es_usepackage):
        ls_tex.append(r'\usepackage{{{}}}'.format(s_usepackage))
    if (b_caption_left):
        ls_tex.append(r'\usepackage{caption}')
        ls_tex.append(r'\captionsetup{justification=raggedright, singlelinecheck=false}')
    ls_tex.append(r'')
    ls_tex.append(r'\title{{{}}}'.format(s_title))
    if not (s_author is None):
        ls_tex.append(r'\author{{{}}}'.format(s_author))
    ls_tex.append(r'')
    ls_tex.append(r'')
    ls_tex.append(r'% begin document')
    ls_tex.append(r'\begin{document}')
    ls_tex.append(r'\maketitle')
    ls_tex.append(r'')

    # output
    return(ls_tex)


def documentclass_beamer(
        s_title,
        s_subtitle = None,
        s_author = 'Elmar Bucher', # None
        s_institute = None,
        s_date = None,
        s_theme = 'default', # 'Singapore'
        s_colortheme = 'default', # 'crane'
        s_fonttheme = 'default', # 'structuresmallcapsserif'
        es_usepackage = {},
    ):
    '''
    input:
    output:
    description:
        generate code for the latex beamer class, with titlepage frame.
        outputs the code as list of strings.
        theme matrix: https://hartwork.org/beamer-theme-matrix/
    '''
    # genrate tex
    ls_tex = []
    ls_tex.append(r'\documentclass{beamer}')
    ls_tex.append(r'\usetheme{{{0}}}'.format(s_theme))
    ls_tex.append(r'\usecolortheme{{{0}}}'.format(s_colortheme))
    ls_tex.append(r'\usefonttheme{{{0}}}'.format(s_fonttheme))
    for s_usepackage in sorted(es_usepackage):
        ls_tex.append(r'\usepackage{{{0}}}'.format(s_usepackage))
    ls_tex.append(r'')
    ls_tex.append(r'\title{{{0}}}'.format(s_title))
    if not (s_subtitle is None):
        ls_tex.append(r'\subtitle{{{0}}}'.format(s_subtitle))
    if not (s_author is None):
        ls_tex.append(r'\author{{{0}}}'.format(s_author))
    if not (s_institute is None):
        ls_tex.append(r'\institute{{{0}}}'.format(s_institute))
    if not (s_date is None):
        ls_tex.append(r'\date{{{0}}}'.format(s_date))
    ls_tex.append(r'')
    ls_tex.append(r'')
    ls_tex.append(r'% begin document')
    ls_tex.append(r'\begin{document}')
    ls_tex.append(r'    \frame{\titlepage}')
    ls_tex.append(r'')

    # output
    return(ls_tex)


###########################
#### end documentclass ####
###########################

def end_document(
        ls_tex,
        ls_software = ['Python3'],
        b_section_poweredby = True,
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        ls_software: list of software libraries, utilized for dataanalysis.
            the default only lists Python3.
        b_section_poweredby: boolean to specify if an section about the
            software used for analysis and document generatiomn shoul be added.
            default is True.

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        fianlizes the latex docuemnt.
        by default this function add a section about the sofware
        used for analysis and this documentation. By default is assumed
        that Python3 was used for analysis, but this can be adjusted with the ls_softare parameter..
    '''
    # update tex
    if (b_section_poweredby):
        ls_tex.append(r'% sofware reference')
        ls_tex.append(r'\section{Software}')
        ls_tex.append(r'{} was utilized for data analysis.'.format(', '.join(ls_software)))
        ls_tex.append(r'Document generation was powered by \LaTeX and Python3.')
        ls_tex.append(r'')
    ls_tex.append(r'% end document')
    ls_tex.append(r'\end{document}')

    # output
    return(ls_tex)


def end_document_beamer(
        ls_tex,
        ls_coauthor = [],
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        ls_coauthor: list of coauthors.
        s_enumitem: sting to set enumitem parameters. e.g. 'noitemsep'

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        fianlizes the latex docuemnt.
        if coauthors are given this function adds a Acknowledgement frame.
    '''
    # update tex
    if (len(ls_coauthor)):
        ls_tex.append(r'% acknowledgement')
        ls_tex.append(r'\begin{frame}')
        ls_tex.append(r'    \frametitle{Acknowledgement}')
        ls_tex.append(r'    \begin{itemize}')
        for s_item in ls_coauthor:
            ls_tex.append(r'    \item {0}'.format(s_item.replace('_','\_')))
        ls_tex.append(r'    \end{itemize}')
        ls_tex.append(r'\end{frame}')
        ls_tex.append(r'')
    ls_tex.append(r'% end document')
    ls_tex.append(r'\end{document}')

    # output
    return(ls_tex)


##############################
#### inside the  document ####
##############################

def section (
        ls_tex,
        s_section,
        s_comment = None
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        s_section: section title string.
        s_comment: latex comment that will preceede the section code.

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate latex section code.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\section{{{}}}'.format(s_section))

    # output
    return(ls_tex)


def subsection (
        ls_tex,
        s_subsection,
        s_comment = None
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        s_subsection: subsection title string.
        s_comment: latex comment that will preceede the subsection code.

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate latex subsection code.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\subsection{{{}}}'.format(s_subsection))

    # output
    return(ls_tex)


def paragraph (
        ls_tex,
        s_paragraph,
        s_comment = None
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        s_paragraph: paragraph title string.
        s_comment: latex comment that will preceede the paragraph code.

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate latex paragraph code.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\paragraph{{{}}}'.format(s_paragraph))

    # output
    return(ls_tex)


def subparagraph (
        ls_tex,
        s_subparagraph,
        s_comment = None
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        s_subparagraph: subparagraph title string.
        s_comment: latex comment that will preceede the subparagraph code.

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate latex subparagraph code.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\subparagraph{{{}}}'.format(s_subparagraph))

    # output
    return(ls_tex)


def begin_frame(
        ls_tex,
        s_frametitle = None,
        s_comment = None,
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        s_frametitle: frame title string.
        s_comment: latex comment that will preceede the frame code

    output:
        ls_tex: updated latex code, stored as list of strings.

    descriiption:
        generate begin frame latex code.
    '''
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\begin{frame}')
    if not(s_frametitle is None):
        ls_tex.append(r'    \frametitle{{{0}}}'.format(s_frametitle.replace('_','\_')))

    # output
    return(ls_tex)


def end_frame(
        ls_tex,
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.

    output:
        ls_tex: updated latex code, stored as list of strings.

    descriiption:
        generate end frame latex code.
    '''
    # generate tex
    ls_tex.append(r'\end{frame}')
    ls_tex.append(r'')

    # output
    return(ls_tex)


def ref(s_label):
    '''
    input:
        s_label: reference label.
        e.g. figure reference label like fig:abc

    output:
        s_reference: apropriate latex syntaxed refernce string.
        something like ~\ref{fig:abc}.

    description:
        generate latex referencode code.
    '''
    s_reference = '~\\ref{{{}}}'.format(s_label)
    # output
    return(s_reference)


def figure(
        ls_tex,
        ls_figure,
        r_height_in = None,
        r_width_in = None,
        s_float = '!htb',
        s_caption = None,
        s_label = None,
        s_comment = None,
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        ls_figure: list of string with file paths to image files.
        r_height_in: real number to stecify the image y size in inches.
        r_width_in: real number to stecify the image x size in inches.
        s_float: string to specify how strictely the images should be placed.
            ! ignores some parameter for placement, h here, t top, b bottom,
            p page with floating objects. default is !htb.
        s_caption: figure caption string
        s_label: figure label for reference. e.g. 'fig:abc'.
        s_comment: latex comment that will preceede the figure code

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate latex figure code, to load images into the document.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    s_height_width = 'keepaspectratio'
    if not (r_width_in is None):
        s_height_width = 'width={}in, {}'.format(r_width_in, s_height_width)
    if not (r_height_in is None):
        s_height_width = 'height={}in, {}'.format(r_height_in, s_height_width)
    ls_tex.append(r'\begin{{figure}}[{}]'.format(s_float))
    for s_figure in ls_figure:
        ls_tex.append(r'  \includegraphics[{}]{{{}}}'.format(s_height_width, s_figure))
    if not (s_caption is None):
        ls_tex.append(r'  \caption{{{}}}'.format(s_caption))
    if not (s_label is None):
        ls_tex.append(r'  \label{{{}}}'.format(s_label))
    ls_tex.append(r'\end{figure}')

    # output
    return(ls_tex)


def enumitem(
        ls_tex,
        ls_item = [],
        s_enumitem = '',  # 'noitemsep'
        s_comment = None,
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        ls_item: list to itemize.
        s_enumitem: sting to set enumitem parameters. e.g. 'noitemsep'
        s_comment: latex comment that will preceede the itemize code

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate enumitem pacakge based item list latex code.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\begin{{enumerate}}[{0}]'.format(s_enumitem))
    for s_item in ls_item:
        ls_tex.append(r'    \item {0}'.format(s_item.replace('_','\_')))
    ls_tex.append(r'\end{enumerate}')

    # output
    return(ls_tex)


def itemize(
        ls_tex,
        ls_item = [],
        s_comment = None,
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        ls_item: list to itemize.
        s_comment: latex comment that will preceede the itemize code

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate item list latex code.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\begin{itemize}')
    for s_item in ls_item:
        ls_tex.append(r'    \item {0}'.format(s_item.replace('_','\_')))
    ls_tex.append(r'\end{itemize}')

    # output
    return(ls_tex)


def enumerate(
        ls_tex,
        ls_item = [],
        s_comment = None,
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        ls_item: list to itemize.
        s_comment: latex comment that will preceede the enumerate code

    output:
        ls_tex: updated latex code, stored as list of strings.

    description:
        generate numerical ordered item list latex code.
    '''
    # generate tex
    if not (s_comment is None):
        ls_tex.append(r'% {}'.format(s_comment))
    ls_tex.append(r'\begin{enumerate}')
    for s_item in ls_item:
        ls_tex.append(r'    \item {0}'.format(s_item.replace('_','\_')))
    ls_tex.append(r'\end{enumerate}')

    # output
    return(ls_tex)


################
#### bibtex ####
################

def bibliography(
        ls_tex,
        s_pathfile_bib,
        s_style_bst='alpha',
    ):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        s_pathfile_bib: bibtex library path and file.
        s_style_bst: bibtex bibliographie style. default is alpha.
            if you wane go fancy try the natbib.sty package.

    outout:
        ls_tex: updated latex code, stored as list of strings.

    description:
        this line of code links a bib library to the document.
        atricles and bookes stored in the bib library file
        can be cited in the text by something silimar like \cite{Label1974}.

        to understand bibtex i recommend to read:
        http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf

        i recommend to genrate your bibtex libray fiel with the jabref software.
        http://www.jabref.org/
    '''
    ls_tex.extend([
        r'\bibliographystyle{{{}}}'.format(s_style_bst),
        r'\bibliography{{{}}}'.format(s_pathfile_bib),
    ])

    # output
    return(ls_tex)


###########################
#### generate document ####
###########################

def write_tex(ls_tex, s_pathfile='./pytex.tex'):
    '''
    input:
        ls_tex: latex code, stored as list of strings.
        s_pathfile: tex file path and filename.

    output:
        tex file

    description:
        generate tex file for ls_tex list of string
    '''
    # write file
    s_path = '/'.join(s_pathfile.split('/')[:-1])
    os.makedirs(s_path, exist_ok=True)
    with open(s_pathfile, 'w') as f:
        f.write('\n'.join(ls_tex))


def pdflatex(s_pathfile, b_bibtex=False):
    '''
    input:
        s_pathfile: tex file path and filename
        b_bibtex: boolean to specify if bibtex citations should be
            typeseted into the final document.

    output:
        pdf document

    description:
        runs the pdflatex unix command
    '''
    # run unix command
    s_pathfile = s_pathfile.replace('\\','/')
    ls_pathfile = s_pathfile.split('/')
    s_texwd = '/'.join(ls_pathfile[:-1])
    s_pwd = os.getcwd()
    os.chdir(s_texwd)
    os.system('pdflatex {}'.format(ls_pathfile[-1]))
    if b_bibtex:
        os.system('bibtex {}'.format(ls_pathfile[-1].replace('.tex','.aux')))
        os.system('pdflatex {}'.format(ls_pathfile[-1]))
        os.system('pdflatex {}'.format(ls_pathfile[-1]))
    os.chdir(s_pwd)


# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="test_file.py">
#   Copyright (c) 2003-2020 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

from __future__ import absolute_import


class TestFile:
    """Test file"""

    @classmethod
    def OnePageCells(cls):
        f = TestFile()
        f.file_name = "one-page.xlsx"
        f.folder = "cells\\"
        return f

    @classmethod
    def OnePagePasswordCells(cls):
        f = TestFile()
        f.file_name = "one-page-password.xlsx"
        f.folder = "cells\\"
        return f

    @classmethod
    def TenPagesCells(cls):
        f = TestFile()
        f.file_name = "ten-pages.xlsx"
        f.folder = "cells\\"
        return f

    @classmethod
    def OnePageDiagram(cls):
        f = TestFile()
        f.file_name = "one-page.vsd"
        f.folder = "diagram\\"
        return f

    @classmethod
    def TenPagesDiagram(cls):
        f = TestFile()
        f.file_name = "ten-pages.vsd"
        f.folder = "diagram\\"
        return f

    @classmethod
    def OnePageEmail(cls):
        f = TestFile()
        f.file_name = "one-page.emlx"
        f.folder = "email\\"
        return f

    @classmethod
    def OnePageHtml(cls):
        f = TestFile()
        f.file_name = "one-page.html"
        f.folder = "html\\"
        return f

    @classmethod
    def OnePageBmp(cls):
        f = TestFile()
        f.file_name = "one-page.bmp"
        f.folder = "images\\"
        return f

    @classmethod
    def OnePagePng(cls):
        f = TestFile()
        f.file_name = "one-page.png"
        f.folder = "images\\"
        return f

    @classmethod
    def OnePagePdf(cls):
        f = TestFile()
        f.file_name = "one-page.pdf"
        f.folder = "pdf\\"
        return f

    @classmethod
    def OnePagePasswordPdf(cls):
        f = TestFile()
        f.file_name = "one-page-password.pdf"
        f.folder = "pdf\\"
        return f

    @classmethod
    def TenPagesPdf(cls):
        f = TestFile()
        f.file_name = "ten-pages.pdf"
        f.folder = "pdf\\"
        return f

    @classmethod
    def OnePageSlides(cls):
        f = TestFile()
        f.file_name = "one-page.pptx"
        f.folder = "slides\\"
        return f

    @classmethod
    def OnePagePasswordSlides(cls):
        f = TestFile()
        f.file_name = "one-page-password.pptx"
        f.folder = "slides\\"
        return f

    @classmethod
    def TenPagesSlides(cls):
        f = TestFile()
        f.file_name = "ten-pages.pptx"
        f.folder = "slides\\"
        return f

    @classmethod
    def OnePageWords(cls):
        f = TestFile()
        f.file_name = "one-page.docx"
        f.folder = "words\\"
        return f

    @classmethod
    def OnePagePasswordWords(cls):
        f = TestFile()
        f.file_name = "one-page-password.docx"
        f.folder = "words\\"
        return f

    @classmethod
    def TenPagesWords(cls):
        f = TestFile()
        f.file_name = "ten-pages.docx"
        f.folder = "words\\"
        return f        

    @classmethod
    def get_test_files(cls):
        return [
            cls.OnePageCells(),
            cls.OnePagePasswordCells(),
            cls.TenPagesCells(),
            #cls.OnePageDiagram(),
            #cls.TenPagesDiagram(),
            cls.OnePageEmail(),
            cls.OnePageHtml(),
            cls.OnePageBmp(),
            cls.OnePagePng(),
            cls.OnePagePdf(),
            cls.OnePagePasswordPdf(),
            cls.TenPagesPdf(),
            #cls.OnePageSlides(),
            cls.OnePagePasswordSlides(),
            #cls.TenPagesSlides(),
            cls.OnePageWords(),
            cls.OnePagePasswordWords(),
            cls.TenPagesWords()
        ]

    @classmethod
    def get_test_files_no_password(cls):
        return [
            cls.OnePageCells(),            
            cls.TenPagesCells(),
            cls.OnePageDiagram(),
            cls.TenPagesDiagram(),
            cls.OnePageEmail(),
            cls.OnePageHtml(),
            cls.OnePageBmp(),
            cls.OnePagePng(),
            cls.OnePagePdf(),            
            cls.TenPagesPdf(),
            cls.OnePageSlides(),            
            cls.TenPagesSlides(),
            cls.OnePageWords(),            
            cls.TenPagesWords()
        ]        

    @classmethod
    def get_test_files_many_pages(cls):
        return [            
            cls.TenPagesCells(),
            cls.TenPagesDiagram(),
            #cls.TenPagesPdf(),
            cls.TenPagesSlides(),
            cls.TenPagesWords()
        ]                


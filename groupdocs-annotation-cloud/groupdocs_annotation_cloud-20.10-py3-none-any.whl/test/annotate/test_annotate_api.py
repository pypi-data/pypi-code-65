# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd">
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

import unittest
import os

from groupdocs_annotation_cloud import *
from test.test_context import TestContext
from test.test_file import TestFile

class TestAnnotateApi(TestContext):
    """AnnotateApi unit tests"""

    def test_a_post_annotations(self):
        for test_file in TestFile.get_test_files():
            path = test_file.folder + test_file.file_name
            request = PostAnnotationsRequest(path, self.GetAnnotationsTestBody())
            self.annotate_api.post_annotations(request)

    def test_b_get_import(self):
        for test_file in TestFile.get_test_files():
            path = test_file.folder + test_file.file_name
            request = GetImportRequest(path)
            response = self.annotate_api.get_import(request)
            self.assertGreater(len(response), 0)

    def test_c_get_export(self):        
        self.get_export_case(TestFile.OnePageEmail())
        self.get_export_case(TestFile.OnePagePng())
        self.get_export_case(TestFile.OnePagePdf())
        self.get_export_case(TestFile.OnePageWords())
        self.get_export_case(TestFile.TenPagesWords(), "Area,Point", True, 2, 5)
        self.get_export_case(TestFile.OnePagePasswordPdf(), None, None, None, None, "password")

    def get_export_case(self, test_file, annotation_types=None, annotated_pages=None, first_page=None, last_page=None, password=None):
        path = test_file.folder + test_file.file_name
        request = GetExportRequest(path, annotation_types, annotated_pages, first_page, last_page, password)
        response = self.annotate_api.get_export(request)
        self.assertGreater(os.path.getsize(response), 0)

    def test_d_delete_annotations(self):
        for test_file in TestFile.get_test_files():
            path = test_file.folder + test_file.file_name
            request = DeleteAnnotationsRequest(path)
            self.annotate_api.delete_annotations(request)              
            
    @staticmethod
    def GetAnnotationsTestBody():
        a = AnnotationInfo()
        a.annotation_position = Point()
        a.annotation_position.x = 852
        a.annotation_position.y = 59.388262910798119
        a.box = Rectangle()
        a.box.x = 375.89276123046875
        a.box.y = 59.388263702392578
        a.box.width = 88.7330551147461
        a.box.height = 37.7290153503418
        a.page_number = 0
        a.pen_color = 1201033
        a.pen_style = "Solid"
        a.pen_width = 1
        a.type = "Area"
        a.creator_name = "Anonym A."
        return [a]


if __name__ == '__main__':
    unittest.main()

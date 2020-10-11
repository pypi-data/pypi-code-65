# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from posts.views import ListView as PostListView
from posts.views import DetailView as PostDetailView
from posts.views import PreviewView as PostPreviewView
from .models import Faq, FaqTranslation


class ListView(PostListView):
    post_model = Faq
    translation_model = FaqTranslation
    template_name = 'faq/list.html'
    object_list_name = 'faq_list'


class DetailView(PostDetailView):
    post_model = Faq
    translation_model = FaqTranslation
    template_name = 'faq/detail.html'
    object_name = 'faq'


class PreviewView(PostPreviewView):
    post_model = Faq
    translation_model = FaqTranslation
    template_name = 'faq/detail.html'
    object_name = 'faq'

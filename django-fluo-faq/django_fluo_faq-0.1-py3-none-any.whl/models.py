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

from django.utils.translation import ugettext_lazy as _
from fluo.db import models
from fluo.urls import reverse
from posts.models import PostModel, PostModelTranslation


class Topic(models.CategoryModel):
    class Meta:
        verbose_name = _('topic')
        verbose_name_plural = _('topics')


class Faq(PostModel):
    topics = models.ManyToManyField(
        Topic,
        verbose_name=_('topics'),
    )

    class Meta:
        verbose_name = _('faq')
        verbose_name_plural = _('faq')

    def get_absolute_url(self):
        return reverse('faq-detail', kwargs={
            'slug': self.translate().slug,
        })

    def get_preview_url(self):
        return reverse('faq-preview', kwargs={
            'slug': self.translate().slug,
            'token': self.uuid,
        })


class FaqTranslation(PostModelTranslation):
    parent = models.ForeignKey(
        Faq,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_('faq'),
    )

    class Meta:
        unique_together = (('parent', 'language'), ('title', 'slug'))
        verbose_name = _('faq translation')
        verbose_name_plural = _('faq translations')

    def __str__(self):
        return '%(parent)s [%(language)s]' % {
            'parent': self.parent,
            'language': self.language,
        }

from DjangoAppCenter.extensions.fields import snowflake
from django.contrib.auth.admin import User
from django.db import models
from pypinyin import lazy_pinyin, Style

from lzlab_blogs.extensions.mdeditor.fields import MDTextField


class MetaModel(models.Model):
    id = snowflake.SnowFlakeField(primary_key=True)
    abbreviation = models.CharField(
        verbose_name="首字母缩写", max_length=255, null=True, blank=True, editable=False)
    pinyin = models.CharField(
        verbose_name="拼音全拼", max_length=255, null=True, blank=True, editable=False)
    create_time = models.DateTimeField(
        verbose_name="创建时间", editable=False, auto_now_add=True)
    update_time = models.DateTimeField(
        verbose_name="更新时间", editable=False, auto_now=True)

    class Meta:
        abstract = True

    def compute_pinyin(self):
        pass

    def save(self):
        self.compute_pinyin()
        super().save()


class Author(MetaModel):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name="关联用户", db_constraint=False,
                                related_name="author")
    alias = models.CharField(verbose_name="笔名", max_length=32, null=True, blank=False)
    moto = models.CharField(verbose_name="座右铭", max_length=64, null=True, blank=True)
    wechat_id = models.CharField(verbose_name="微信ID", max_length=64, null=True, blank=True)

    def __str__(self):
        return self.alias.strip()

    def compute_pinyin(self):
        if not self.alias:
            return

        self.abbreviation = ''.join(lazy_pinyin(
            self.alias, style=Style.FIRST_LETTER, errors='ignore')).upper()[0:255]  # 0-255截断 以防太长
        self.pinyin = ''.join(lazy_pinyin(self.alias, errors='ignore'))[0:255]

    class Meta:
        verbose_name = "作者"
        verbose_name_plural = "作者"
        db_table = "blogs_author"


class Topic(MetaModel):
    author = models.ForeignKey(verbose_name="创建作者", to=Author, on_delete=models.CASCADE, db_constraint=False,
                               related_name="topic")
    title = models.CharField(verbose_name="标题", max_length=64)
    public = models.BooleanField(verbose_name="是否公开", default=False)
    foreword = MDTextField(verbose_name="序言")

    def __str__(self):
        return self.title

    def 作者(self):
        return self.author.alias

    def compute_pinyin(self):
        if not self.title:
            return

        self.abbreviation = ''.join(lazy_pinyin(
            self.title, style=Style.FIRST_LETTER, errors='ignore')).upper()[0:255]  # 0-255截断 以防太长
        self.pinyin = ''.join(lazy_pinyin(self.title, errors='ignore'))[0:255]

    class Meta:
        verbose_name = "主题"
        verbose_name_plural = "主题"
        db_table = "blogs_topic"


class Set(MetaModel):
    author = models.ForeignKey(verbose_name="创建作者", to="Author", on_delete=models.CASCADE, db_constraint=False,
                               related_name="set")
    topic = models.ForeignKey(verbose_name="隶属主题", to="Topic", on_delete=models.CASCADE, db_constraint=False,
                              related_name="set")
    title = models.CharField(verbose_name="标题", max_length=64)
    foreword = MDTextField(verbose_name="概述")

    def __str__(self):
        return self.title

    def 作者(self):
        return self.author.alias

    def 主题(self):
        return self.topic.title

    def compute_pinyin(self):
        if not self.title:
            return

        self.abbreviation = ''.join(lazy_pinyin(
            self.title, style=Style.FIRST_LETTER, errors='ignore')).upper()[0:255]  # 0-255截断 以防太长
        self.pinyin = ''.join(lazy_pinyin(self.title, errors='ignore'))[0:255]

    class Meta:
        verbose_name = "文集"
        verbose_name_plural = "文集"
        db_table = "blogs_set"


class Article(MetaModel):
    author = models.ForeignKey(verbose_name="作者", to="Author", on_delete=models.CASCADE, db_constraint=False,
                               related_name="article")
    topic = models.ForeignKey(verbose_name="隶属主题", to="Topic", on_delete=models.CASCADE, null=True, blank=True,
                              db_constraint=False,
                              related_name="article")
    set = models.ForeignKey(verbose_name="隶属文集", to="Set", on_delete=models.CASCADE, db_constraint=False,
                            null=True, blank=True, related_name="article")
    title = models.CharField(verbose_name="标题", max_length=64)
    public = models.BooleanField(verbose_name="是否公开", default=False)
    summary = models.TextField(verbose_name="摘要")
    body = MDTextField(verbose_name="正文")

    def __str__(self):
        return self.title

    def 作者(self):
        return self.author.alias

    def 主题(self):
        if self.topic:
            return self.topic.title
        return ''

    def 文集(self):
        if self.set:
            return self.set.title
        return ''

    def compute_pinyin(self):
        if not self.title:
            return

        self.abbreviation = ''.join(lazy_pinyin(
            self.title, style=Style.FIRST_LETTER, errors='ignore')).upper()[0:255]  # 0-255截断 以防太长
        self.pinyin = ''.join(lazy_pinyin(self.title, errors='ignore'))[0:255]

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        db_table = "blogs_article"

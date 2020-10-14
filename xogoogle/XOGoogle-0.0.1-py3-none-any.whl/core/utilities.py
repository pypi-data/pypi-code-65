#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re


def clean_data(data: str) -> str:
    data = data.lower()
    data = re.sub(
        r'(#\w+; )|({[^}]+})|(\.[\w\-:\(\)=,;\[\]]+)|((\/\/|URL:)*(http|www)[s//:]*[\w./\-%@?=]*)', ' ', data)
    data = re.sub(r'(\$[\w]+)', ' ', data)
    data = re.sub(r'(__[\w]+)', ' ', data)
    data = re.sub(r'\([^\)]+\)', ' ', data)
    data = re.sub(r'([\w=\}\)\(]+;)|(\\[\w]+)|(\w+=\w+)', ' ', data)
    data = re.sub(r'(\*[^\*]+\*)|([\w]+\/[\w]+):|([\/\/]*<[^\>]+>)', ' ', data)
    data = re.sub(r'(\*[^\*]+\*)|([\w]+\/[\w]+):|([\/\/]*<[^\>]+>)', ' ', data)
    data = re.sub(r'\*[\w]+', ' ', data)
    data = re.sub(r'(\+[\d\w\–\-]+)', ' ', data)
    data = re.sub(r' ([\d\–\-_\+]+) ', ' ', data)
    data = re.sub(r' ([\d\–\-_\+]+) ', ' ', data)
    data = re.sub(r'\s{2,}', ' ', data)
    return data

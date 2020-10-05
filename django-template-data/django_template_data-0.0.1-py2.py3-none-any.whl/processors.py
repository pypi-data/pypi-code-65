from template_data.models import *
from django.urls import resolve
from django.db.models import Q
import re


def load_data(request):
    url_name = resolve(request.path_info).url_name
    if not url_name:
        url_name = request.path
        
    tpl_datas = list(TemplateData.objects.filter(Q(page='global')|\
                        (Q(page=url_name))))
    needed_pages = [tpl_data.inherit_page for tpl_data in tpl_datas \
                    if tpl_data.inherit_page != None]
    needed_datas = {(tpl_data.key, tpl_data.page):tpl_data.get_value() for \
                tpl_data in TemplateData.objects.filter(page__in=needed_pages)}
    
    res = {}
    for tpl_data in tpl_datas:
        if not tpl_data.inherit_page:
            res[tpl_data.key] = tpl_data.get_value()
        else:
            tmp_value = tpl_data.get_value()
            res[tpl_data.key] = re.sub("{{ *super *}}", 
                            needed_datas[(tpl_data.key, tpl_data.inherit_page)],
                            tmp_value)
        
    return res   

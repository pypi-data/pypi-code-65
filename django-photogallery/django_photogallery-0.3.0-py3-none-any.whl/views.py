from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import PicturePost
# Create your views here.

class PhotoIndexView(generic.ListView):
    model = PicturePost
    template_name = 'photogallery/index.html'
    context_object_name = 'pictures_list'
    ordering = ['-pub_date']
    paginate_by = 8

class PhotoDetailView(generic.DetailView):
    model = PicturePost
    template_name = 'photogallery/detail.html'
    context_object_name = 'picture'

def go_to_prev(request, picturepost_id):
    picturepost = get_object_or_404(PicturePost, pk=picturepost_id)
    prev_post = PicturePost.objects.filter(id__lt=picturepost.id).last()
    if prev_post:
        return HttpResponseRedirect(reverse('photogallery:detail', args=(prev_post.id,)))
    else:
        return HttpResponseRedirect(reverse('photogallery:detail', args=(picturepost.id,)))


def go_to_next(request, picturepost_id):
    picturepost = get_object_or_404(PicturePost, pk=picturepost_id)
    next_post = PicturePost.objects.filter(id__gt=picturepost.id).first()
    if next_post:
        return HttpResponseRedirect(reverse('photogallery:detail', args=(next_post.id,)))
    else:
        return HttpResponseRedirect(reverse('photogallery:detail', args=(picturepost.id,)))

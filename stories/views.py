
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from .models import Story

from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.utils.views import render, paginate
from mezzanine.utils.models import get_user_model

User = get_user_model()

def index(request):
    stories = Story.objects.all()
    context = {'stories': stories}
    return render(request, 'stories/index.html', context)
    
def detail(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    context = {"story": story}
    return render(request, 'stories/detail.html', context)
        
def stories(request):
    stories = Story.objects.filter(mtype='story')
    context = {'stories': stories}
    return render(request, 'stories/index.html', context)
    
    
def poems(request):
    stories = Story.objects.filter(mtype='poem')
    context = {'stories': stories}
    return render(request, 'stories/index.html', context)
    
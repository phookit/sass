
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from .models import Dog

from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.utils.views import render, paginate
from mezzanine.utils.models import get_user_model

User = get_user_model()

def index(request):
    dogs = Dog.objects.all()
    if len(dogs) == 0:
        dogs = None
    context = {'dogs': dogs}
    return render(request, 'dogs/index.html', context)
    
def detail(request, dog_id):
    dog = get_object_or_404(Dog, pk=dog_id)
    context = {"dog": dog}
    return render(request, 'dogs/detail.html', context)
        
def available(request):
    dogs = Dog.objects.filter(state='available')
    context = {'dogs': dogs}
    return render(request, 'dogs/index.html', context)
        
def rehomed(request):
    dogs = Dog.objects.filter(state='rehomed')
    context = {'dogs': dogs}
    return render(request, 'dogs/index.html', context)

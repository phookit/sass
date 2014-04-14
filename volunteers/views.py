
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from .models import Volunteer
from .forms import VolunteerForm

from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.utils.views import render, paginate
from mezzanine.utils.models import get_user_model

User = get_user_model()

def index(request):
    if request.user.has_perm('volunteers.add_volunteer'):
        return render(request, 'volunteers/index_admin.html', {'volunteers': Volunteer.objects.filter(validated=True)})
        
    return render(request, 'volunteers/index.html', {})

    
def detail(request, volunteer_id):
    if request.user.has_perm('volunteers.add_volunteer'):
        context = {"volunteer": get_object_or_404(Volunteer, pk=volunteer_id) }
    else:
        return HttpResponseRedirect('/volunteers/')
    return render(request, 'volunteers/detail.html', context)
        
    
def application(request):
    if request.method == 'POST': # If the form has been submitted...
        form = VolunteerForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form.save()
            return HttpResponseRedirect('/volunteers/thanks') # Redirect after POST
    else:
        form = VolunteerForm() # An unbound form
        
    return render(request, 'volunteers/application.html', {
        'form': form,
    })

    


def application_thanks(request):
    return render(request, 'volunteers/thanks.html', {})


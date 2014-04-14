
from django.http import Http404
from django.shortcuts import get_object_or_404


from .models import Supporter

from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.utils.views import render, paginate
from mezzanine.utils.models import get_user_model

User = get_user_model()


def index(request):
    supporters = Supporter.objects.filter(visible=True)
    context = {'supporters': supporters}
    return render(request, 'supporters/index.html', context)



def detail(request, supporter_id):
    supporter = get_object_or_404(Supporter, pk=supporter_id)
    context = {"supporter": supporter}
    return render(request, 'supporters/detail.html', context)


from django.shortcuts import render
from .models import Kitob
# Create your views here.

def kitoblar_royhati(request):
    kitoblar = Kitob.objects.all()
    context = {
        'kitoblar':kitoblar
    }
    return render(request, 'books/kitoblar.html',context)
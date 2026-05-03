from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.decorators import login_required
from books.models import Kitob, Almashitirish

# Create your views here.

@login_required
def profil(request):
    mening_kitoblarim = request.user.books.all()
    kelgan_sorovlar = Almashitirish.objects.filter(
        kitob__ega = request.user,
        holat = 'kutilmoqda'
    )
    yuborilgan_sorovlar = Almashitirish.objects.filter(yuboruvchi=request.user)
    context = {
        'mening_kitoblarim':mening_kitoblarim,
        'kelgan_sorovlar':kelgan_sorovlar,
        'yuborilgan_sorovlar':yuborilgan_sorovlar
    }
    return render(request,'accounts/profil.html',context)

def royhatdan_otish(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('kitoblar-royhati')
            
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {"form":form})

def kirish(request):
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('kitoblar-royhati')
    else:
        form = AuthenticationForm()
    return render(request,'accounts/login.html',{'form':form})
        
def chiqish(request):
    logout(request)
    return redirect('kirish')


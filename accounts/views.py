from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

# Create your views here.

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
    return render(request,'accounts/login.html',{'from':form})
        
def chiqish(request):
    logout(request)
    return redirect('kirish')
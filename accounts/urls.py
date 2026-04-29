from django.urls import path,include
from . import views
urlpatterns = [
    path('register/', views.royhatdan_otish, name='royxatdan-otish'),
    path('login/',views.kirish, name='kirish'),
    path('logout/',views.chiqish, name='chiqish')
]
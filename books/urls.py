from django.urls import path
from . import views

urlpatterns = [
    path('',views.kitoblar_royhati, name='kitoblar-royhati'),
    path('qoshish/',views.kitob_qoshish,name='kitob-qoshish'),
    path('kitob/<int:kitob_id>/', views.kitob_detail, name='kitob-detail'),
    path('kitob/<int:kitob_id>/tahrirlash/', views.kitob_tahrirlash, name='kitob-tahrirlash'),
    path('kitob/<int:kitob_id>/ochirish/', views.kitob_ochirish, name='kitob-ochirish'),
    path('sevimli/<int:kitob_id>/', views.sevimli_toggle, name='sevimli-toggle'),
    path('sevimlilar/', views.sevimlilar, name='sevimlilar'),
    path('sorov/<int:kitob_id>/',views.sorov_yuborish,name='sorov-yuborish'),
    path('sorov/<int:sorov_id>/qabul/',views.sorov_qabul,name='sorov-qabul'),
    path('sorov/<int:sorov_id>/rad/',views.sorov_rad,name='sorov-rad'),
]
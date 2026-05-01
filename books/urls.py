from django.urls import path
from . import views

urlpatterns = [
    path('',views.kitoblar_royhati, name='kitoblar-royhati'),
    path('qoshish/',views.kitob_qoshish,name='kitob-qoshish'),
    path('sorov/<int:kitob_id>/',views.sorov_yuborish,name='sorov-yuborish')
]
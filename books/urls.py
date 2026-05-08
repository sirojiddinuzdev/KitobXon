from django.urls import path
from . import views

urlpatterns = [
    path('',views.kitoblar_royhati, name='kitoblar-royhati'),
    path('qoshish/',views.kitob_qoshish,name='kitob-qoshish'),
    path('sorov/<int:kitob_id>/',views.sorov_yuborish,name='sorov-yuborish'),
    path('sorov/<int:sorov_id>/qabul/',views.sorov_qabul,name='sorov-qabul'),
    path('sorov/<int:sorov_id>/rad/',views.sorov_rad,name='sorov-rad')
]
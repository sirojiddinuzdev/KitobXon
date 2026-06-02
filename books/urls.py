from django.urls import path
from . import views

urlpatterns = [
    path('',views.kitoblar_royhati, name='kitoblar-royhati'),
    path('qoshish/',views.kitob_qoshish,name='kitob-qoshish'),
    path('kitob/<int:kitob_id>/tahrirlash/', views.kitob_tahrirlash, name='kitob-tahrirlash'),
    path('kitob/<int:kitob_id>/ochirish/', views.kitob_ochirish, name='kitob-ochirish'),
    path('sorov/<int:kitob_id>/',views.sorov_yuborish,name='sorov-yuborish'),
    path('sorov/<int:sorov_id>/qabul/',views.sorov_qabul,name='sorov-qabul'),
    path('sorov/<int:sorov_id>/rad/',views.sorov_rad,name='sorov-rad'),

    path('api/kitoblar/',views.KitobListAPI.as_view(),name='api-kitoblar'),
    path('api/kitoblar/<int:pk>/',views.KitobDetailAPI.as_view(),name='api-kitoblar-detail'),
    path('api/mening-kitoblarim/',views.MeningKitoblarimAPI.as_view(),name='api-mening-kitoblarim'),
    path('api/sorovlar/',views.AlmashitirishListAPI.as_view(),name='api-sorovlar'),
]
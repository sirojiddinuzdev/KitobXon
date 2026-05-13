from rest_framework import serializers
from .models import Kitob,Almashitirish

class KitobSerializer(serializers.ModelSerializer):
    ega= serializers.StringRelatedField()

    class Meta:
        model = Kitob
        fields = ['id','nomi','muallif','janr','hudud','tavsif','rasm','mavjud','ega','yaratildi']

class AlmashitirishSerializer(serializers.ModelSerializer):
    yuboruvchi = serializers.StringRelatedField
    kitob = KitobSerializer()

    class Meta:
        fields = ['id','kitob','yuboruvchi','holat','yaratildi']
from django.db.models import Avg
from rest_framework import serializers

from .models import Kitob, Almashitirish, Sevimli, Sharh


class SharhSerializer(serializers.ModelSerializer):
    muallif = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Sharh
        fields = ['id', 'muallif', 'baho', 'matn', 'yaratildi']
        read_only_fields = ['id', 'muallif', 'yaratildi']


class KitobSerializer(serializers.ModelSerializer):
    ega = serializers.StringRelatedField(read_only=True)
    janr_nomi = serializers.CharField(source='get_janr_display', read_only=True)
    hudud_nomi = serializers.CharField(source='get_hudud_display', read_only=True)
    ortacha_baho = serializers.SerializerMethodField()
    sharh_soni = serializers.SerializerMethodField()

    class Meta:
        model = Kitob
        fields = [
            'id', 'nomi', 'muallif', 'tavsif',
            'janr', 'janr_nomi', 'hudud', 'hudud_nomi',
            'rasm', 'mavjud', 'ega', 'yaratildi',
            'ortacha_baho', 'sharh_soni',
        ]
        read_only_fields = ['id', 'ega', 'mavjud', 'yaratildi']

    def get_ortacha_baho(self, obj) -> float:
        v = getattr(obj, 'avg_baho', None)
        if v is None:
            v = obj.sharhlar.aggregate(a=Avg('baho'))['a']
        return round(v, 1) if v else 0

    def get_sharh_soni(self, obj) -> int:
        v = getattr(obj, 'sharh_soni_ann', None)
        if v is None:
            v = obj.sharhlar.count()
        return v


class AlmashitirishSerializer(serializers.ModelSerializer):
    yuboruvchi = serializers.StringRelatedField(read_only=True)
    kitob = KitobSerializer(read_only=True)
    holat_nomi = serializers.CharField(source='get_holat_display', read_only=True)

    class Meta:
        model = Almashitirish
        fields = ['id', 'kitob', 'yuboruvchi', 'holat', 'holat_nomi', 'yaratildi']
        read_only_fields = ['id', 'yuboruvchi', 'holat', 'yaratildi']


class SevimliSerializer(serializers.ModelSerializer):
    kitob = KitobSerializer(read_only=True)

    class Meta:
        model = Sevimli
        fields = ['id', 'kitob', 'yaratildi']
        read_only_fields = ['id', 'yaratildi']

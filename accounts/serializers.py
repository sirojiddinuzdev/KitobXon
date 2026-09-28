from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import Profil, Bildirishnoma,TasdiqlashKodi



class ProfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profil
        fields = ['username', 'avatar', 'bio', 'telegram', 'telefon', 'instagram']


class UserSerializer(serializers.ModelSerializer):
    profil = ProfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profil']


class BildirishnomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bildirishnoma
        fields = ['id', 'matn', 'havola', 'turi', 'oqilgan', 'yaratildi']
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        Profil.objects.get_or_create(user=user)
        return user
    
class TasdiqlashSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    kod = serializers.CharField(max_length=6)

    def validate(self, data):
        from .services import tasdiqlash_kodi_tekshirish_service
        from django.core.exceptions import ValidationError
        try:
            user, tasdiqlash = tasdiqlash_kodi_tekshirish_service(data['user_id'], data['kod'])
            data['user'] = user
            data['tasdiqlash'] = tasdiqlash
        except ValidationError as e:
            raise serializers.ValidationError(str(e.message if hasattr(e, 'message') else e))
        return data
    
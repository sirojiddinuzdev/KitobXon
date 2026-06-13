from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

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
        try:
            tasdiqlash = TasdiqlashKodi.objects.get(
                user_id=data['user_id'],
                kod=data['kod'],
                tasdiqlangan=False
            )
            data['tasdiqlash'] = tasdiqlash
        except TasdiqlashKodi.DoesNotExist:
            raise serializers.ValidationError("Kod noto'g'ri yoki eskirgan!")
        return data
    
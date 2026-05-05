from django import forms
from .models import Profil

class ProfilForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['telefon', 'telegram', 'instagram']
        widgets = {
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 12 345 67 89'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
        }
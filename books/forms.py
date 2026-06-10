from django import forms
from .models import Kitob, Istak

class KitobForm(forms.ModelForm):
    class Meta:
        model = Kitob
        fields = ['muallif', 'nomi', 'janr', 'tavsif', 'rasm','hudud']
        widgets = {
            'nomi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kitob nomi'}),
            'muallif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Muallif'}),
            'janr': forms.Select(attrs={'class': 'form-select'}),
            'tavsif': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kitob haqida'}),
            'rasm': forms.FileInput(attrs={'class': 'form-control'}),
            'hudud':forms.Select(attrs={'class':'form-select'})
        }


class IstakForm(forms.ModelForm):
    class Meta:
        model = Istak
        fields = ['nomi', 'muallif', 'izoh']
        widgets = {
            'nomi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Izlayotgan kitob nomi'}),
            'muallif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Muallif (ixtiyoriy)'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Qo‘shimcha izoh (ixtiyoriy)'}),
        }
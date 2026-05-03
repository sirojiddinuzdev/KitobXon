from django import forms
from .models import Kitob

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
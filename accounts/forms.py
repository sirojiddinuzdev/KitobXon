from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Profil

PASSWORD_VALIDATION_MESSAGES = {
    'password_too_similar': _("Parol shaxsiy ma'lumotlaringizga juda o'xshamasligi kerak."),
    'password_too_short': _("Parol kamida 8 ta belgidan iborat bo'lishi kerak."),
    'password_too_common': _("Parol keng tarqalgan parollardan biri bo'lmasligi kerak."),
    'password_entirely_numeric': _("Parol faqat raqamlardan iborat bo'lmasligi kerak."),
}

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        labels = {
            'username': _('Foydalanuvchi nomi'),
            'password1': _('Parol'),
            'password2': _('Parolni tasdiqlash'),
        }
        help_texts = {
            'username': _(
                'Majburiy. 150 belgidan kam. Harflar, raqamlar va @/./+/-/_ belgilaridan foydalanishingiz mumkin.'
            ),
            'password2': _('Oldingi parolni qayta kiriting.'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Foydalanuvchi nomi'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parolni tasdiqlash'
        })
        self.fields['password1'].help_text = (
            '<ul class="form-text text-muted small mb-0">'
            '<li>Parol shaxsiy maʼlumotlaringizga juda o‘xshamasligi kerak.</li>'
            '<li>Parol kamida 8 ta belgidan iborat bo‘lishi kerak.</li>'
            '<li>Parol keng tarqalgan parollardan biri bo‘lmasligi kerak.</li>'
            '<li>Parol faqat raqamlardan iborat bo‘lmasligi kerak.</li>'
            '</ul>'
        )

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password(password1, self.instance)
            except ValidationError as exc:
                errors = []
                for error in exc.error_list:
                    errors.append(PASSWORD_VALIDATION_MESSAGES.get(error.code, error.message))
                raise ValidationError(errors)
        return password1

class ProfilForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['telefon', 'telegram', 'instagram']
        widgets = {
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 12 345 67 89'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
        }
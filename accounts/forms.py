from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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
    email = forms.EmailField(
        required=True,
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Bu email allaqachon ro'yxatdan o'tgan."))
        return email

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

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Foydalanuvchi nomi')
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Foydalanuvchi nomi'})
        self.fields['password'].label = _('Parol')
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Parol'})


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['avatar', 'bio', 'telefon', 'telegram', 'instagram']
        labels = {
            'avatar': _('Profil rasmi'),
            'bio': _('O‘zingiz haqingizda'),
            'telefon': _('Telefon'),
            'telegram': _('Telegram'),
            'instagram': _('Instagram'),
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Qisqacha o‘zingiz haqingizda...'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 12 345 67 89'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
        }

class TasdiqlashForm(forms.Form):
    kod = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '6 xonali kodni kiriting'
        })
    )

from django.contrib.auth.models import User

class RoyxatForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parol'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parolni tasdiqlang'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Parollar mos kelmadi!')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="البريد الإلكتروني")
    first_name = forms.CharField(max_length=150, required=False, label="الاسم الأول")
    last_name = forms.CharField(max_length=150, required=False, label="اسم العائلة")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد مستخدم من قبل")
        return email

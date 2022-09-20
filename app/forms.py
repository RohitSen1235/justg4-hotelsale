from dataclasses import field
from site import USER_SITE
from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField() 

    class Meta:
        model = User
        fields =['username','first_name','last_name','email','password1','password2']



class LoginForm(forms.Form):
    
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)
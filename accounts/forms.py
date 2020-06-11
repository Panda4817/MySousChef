from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


# Registration form, based on User model
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required')
    accept_polices = forms.BooleanField()

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password1',
            'password2',
        )

# Contact form for contact page
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    cc_myself = forms.BooleanField(required=False)
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Subject'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Message'
    }))

# Update username form
class ChangeUsernameForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Username',
    }), label='New Username', required=True, help_text="150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    class Meta:
        model = User
        fields = (
            'username',
        )


# Update email form
class ChangeEmailForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Email',
    }), label='New Email', required=True, help_text="Note: You will need to verify your new email address.")
    class Meta:
        model = User
        fields = (
            'email',
        )
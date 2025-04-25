from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class UserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')  
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('El email introducido ya está registrado, ¡debes introducir otro!')
        return email
    

from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ( 'username', 'nombre')


    def clean_email(self):
        email = self.cleaned_data.get('email')  
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('El email introducido ya está registrado, ¡debes introducir otro!')
        return email

class UserUpdateProfilelForm(forms.ModelForm):

    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),required=False)
    imagen_perfil = forms.ImageField(required=False) 
    banner_perfil = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('nombre','fecha_nacimiento', 'genero','posicion','ubicacion', 'imagen_perfil', 'banner_perfil' )

    def __init__(self, *args, **kwargs):

        super(UserUpdateProfilelForm, self).__init__(*args, **kwargs)
        
        self.fields['nombre'].widget.attrs.update({'placeholder': 'Tu nombre completo'})

        self.fields['ubicacion'].widget.attrs.update({'placeholder': 'Ciudad, Provincia'})
        
    

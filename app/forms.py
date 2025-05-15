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

class PartidoForm(forms.ModelForm):
    
    fecha = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control bg-dark text-white border-secondary'}),
        label="Fecha y Hora del Partido"
    )
    # el campo del form pista usara un ModelChoiceField por defecto, que renderiza como un <select>
    cancha = forms.ModelChoiceField(
        queryset=Cancha.objects.filter(disponible=True).order_by('nombre_cancha'), # Mostrar solo canchas disponibles
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Cancha"
    )
    tipo = forms.ChoiceField(
        choices=Partido.TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Tipo de Partido (Formato)"
    )
    
    NIVEL_CHOICES = [ 
        ('', 'Cualquier nivel'),
        ('PRINCIPIANTE', 'Principiante'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
        ('PRO', 'Profesional/Muy Alto'),
    ]
    nivel = forms.ChoiceField(
        choices=NIVEL_CHOICES,
        required=False, #
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Nivel Estimado"
    )

    modalidad = forms.ChoiceField(
        choices=Partido.MODALIDAD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Modalidad"
    )

    max_jugadores = forms.IntegerField(
        min_value=2, #aunque ya lo tengo en bbdd es bueno tenerlo aqui tmbien
        widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Ej: 10'}),
        label="Máximo de Jugadores"
    )
    costo = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': '0.00'}),
        label="Costo por Jugador (€)"
    )


    metodo_pago = forms.ChoiceField(
        choices=Partido.METODO_PAGO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Método de Pago"
    )

    comentarios = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Reglas especiales, qué color deben llevar los equipos, etc...'}),
        label="Comentarios Adicionales"
    )

    class Meta:
        model = Partido
        fields = [
            'fecha', 'cancha', 'tipo', 'nivel', 'modalidad',
            'max_jugadores', 'costo', 'metodo_pago', 'comentarios'
        ]

        
    

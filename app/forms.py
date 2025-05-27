from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone as django_timezone
from datetime import datetime, time, timezone
from django.utils.timezone import make_aware

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
    
    dia_partido = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control bg-dark text-white border-secondary',
                
            }
        ),
        label="Día del Partido"
    )

    HORARIOS_CHOICES = [] #PONER TAMBIEN EN EL MODELO
    for hora in range(10, 23): 
        HORARIOS_CHOICES.append((time(hora, 0).strftime('%H:%M'), f"{hora:02d}:00"))
        

    hora_inicio_partido = forms.ChoiceField(
        choices=HORARIOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Hora de Inicio del Partido"
    )

    cancha = forms.ModelChoiceField(
        queryset=Cancha.objects.filter(disponible=True).order_by('nombre_cancha'),
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Cancha",
        empty_label="Selecciona una cancha"
    )
    
    nivel = forms.ChoiceField(
        choices=Partido.NIVEL_CHOICES,
        required=False,
        widget=forms.Select(),
        label="Nivel Estimado del Partido"
    )

    class Meta:
        model = Partido
        fields = [
            'cancha', 'tipo', 'nivel', 'modalidad',
            'max_jugadores', 'costo', 'metodo_pago', 'comentarios'
        ]

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get('dia_partido')
        hora_str = cleaned_data.get('hora_inicio_partido') 
        cancha = cleaned_data.get('cancha')

        dia_limite_str = cleaned_data.get('fecha_limite_inscripcion_dia')
        hora_limite_str = cleaned_data.get('fecha_limite_inscripcion_hora')


        if not dia:
            self.add_error('dia_partido', "Debes seleccionar un día para el partido.")
            return cleaned_data
        
        if not hora_str:
            self.add_error('hora_inicio_partido', "Debes seleccionar una hora de inicio.")
            return cleaned_data

        # Convertir la hora_str a un objeto time
        try:
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            self.add_error('hora_inicio_partido', "Hora de inicio inválida.")
            return cleaned_data

        # Combinar día y hora para crear el datetime de inicio
        naive_datetime = datetime.combine(dia, hora_obj)
        fecha_inicio = make_aware(naive_datetime)

        # Validar que la fecha de inicio no sea en el pasado
        if fecha_inicio < django_timezone.now():
            self.add_error('dia_partido', 'La fecha y hora de inicio del partido no puede ser en el pasado.')
            self.add_error('hora_inicio_partido', 'La fecha y hora de inicio del partido no puede ser en el pasado.')
            return cleaned_data # Detener si la fecha es inválida

        # Guardar el datetime combinado en cleaned_data para que la vista lo use
        cleaned_data['fecha'] = fecha_inicio

        if dia_limite_str and hora_limite_str: # Si el usuario proporcionó ambos
            try:
                hora_limite_obj = datetime.strptime(hora_limite_str, '%H:%M').time()
                naive_limite_dt = datetime.combine(dia_limite_str, hora_limite_obj)
                fecha_limite = django_timezone.make_aware(naive_limite_dt)
                if fecha_limite >= fecha_inicio:
                    self.add_error('fecha_limite_inscripcion_dia', 'La fecha límite de inscripción debe ser anterior a la fecha del partido.')
                else:
                    cleaned_data['fecha_limite_inscripcion'] = fecha_limite
            except ValueError:
                self.add_error('fecha_limite_inscripcion_hora', 'Hora límite de inscripción inválida.')
        elif dia_limite_str or hora_limite_str: # Si solo proporcionó uno
             self.add_error('fecha_limite_inscripcion_dia', 'Debes proporcionar tanto el día como la hora para la fecha límite, o dejar ambos en blanco para usar el valor por defecto (1h antes del partido).')
        else:
            # Si se dejan en blanco, el modelo lo calculará en save()
            cleaned_data['fecha_limite_inscripcion'] = None # Indicar que se use el default del modelo/save

        
        if cancha: 
            fecha_fin_propuesta = fecha_inicio + timedelta(hours=1)

            partidos_conflictivos_query = Partido.objects.filter(
                cancha=cancha,
                estado__in=['PROGRAMADO', 'EN_CURSO'],
                fecha__lt=fecha_fin_propuesta, 
            )

            if self.instance and self.instance.pk: 
                partidos_conflictivos_query = partidos_conflictivos_query.exclude(pk=self.instance.pk)
            
            for partido_existente in partidos_conflictivos_query:
                fin_existente = partido_existente.fecha + timedelta(hours=1)
                if fin_existente > fecha_inicio:
                    self.add_error('hora_inicio_partido', forms.ValidationError(
                        f"La cancha '{cancha.nombre_cancha}' ya está reservada de "
                        f"{partido_existente.fecha.strftime('%H:%M')} a {fin_existente.strftime('%H:%M')} "
                        f"el {partido_existente.fecha.strftime('%d/%m/%Y')}. "
                        f"Por favor, elige otro horario o cancha.",
                        code='solapamiento'
                    ))
                    self.add_error('cancha', "Horario no disponible.")
                    break 
        
        # Lógica de costo y método de pago 
        costo = cleaned_data.get("costo")
        metodo_pago = cleaned_data.get("metodo_pago")
        if costo is not None:
            if costo > 0 and metodo_pago == 'GRATIS':
                self.add_error('metodo_pago', 'Si el partido tiene un costo, el método de pago no puede ser "Gratis".')
            elif costo == 0 and metodo_pago != 'GRATIS' and metodo_pago is not None:
                 cleaned_data['metodo_pago'] = 'GRATIS'
        elif metodo_pago != 'GRATIS' and metodo_pago is not None:
             self.add_error('costo', 'Debes especificar un costo o seleccionar "Gratis" como método de pago si el campo costo está vacío.')

        return cleaned_data
    
class CanchasForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre_cancha', 'ubicacion', 'tipo', 'propiedad', 'superficie',
                 'costo_partido', 'descripcion', 'disponible', 'imagen']
        
        def __init__(self, *args, **kwargs):
            super(CanchasForm, self).__init__(*args, **kwargs)
        
            # Nombres personalizados para los campos
            self.fields['nombre_cancha'].label = "Nombre de la cancha"
            self.fields['ubicacion'].label = "Dirección completa"
            self.fields['tipo'].label = "Tipo de cancha"
            self.fields['propiedad'].label = "Tipo de propiedad"
            self.fields['costo_por_hora'].label = "Precio por hora"
            self.fields['descripcion'].label = "Descripción"
            self.fields['disponible'].label = "Disponible para reservas"
            self.fields['imagen'].label = "Imagen de la cancha"
        

        
    

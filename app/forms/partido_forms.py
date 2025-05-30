from datetime import datetime, time, timedelta
from django import forms
from app.models.cancha import Cancha
from app.models.equipo import Equipo
from app.models.partido import Partido
from django.db.models import Q


from django.utils import timezone as django_timezone
from django.utils.timezone import make_aware


# PartidoForm && ResultadoPartidoForm


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
    equipo_local = forms.ModelChoiceField(
        queryset=Equipo.objects.filter(tipo_equipo='PERMANENTE', activo=True), 
        required=False,
        label="Equipo Local (Opcional)",
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        empty_label=" (Ninguno - Partido Abierto/Equipos por formar)"
    )

    equipo_visitante = forms.ModelChoiceField(
        queryset=Equipo.objects.filter(tipo_equipo='PERMANENTE', activo=True), 
        required=False,
        label="Equipo Visitante (Opcional)",
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        empty_label=" (Ninguno - Partido Abierto/Equipos por formar)"
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
            'max_jugadores', 'costo', 'metodo_pago', 'comentarios',
            'equipo_local', 'equipo_visitante'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        #para 'equipo_local', solo los equipos del usuario
        if self.user:
            self.fields['equipo_local'].queryset = Equipo.objects.filter(
                Q(capitan=self.user) | Q(jugadores=self.user),
                tipo_equipo='PERMANENTE', activo=True
            ).distinct().order_by('nombre_equipo')


    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get('dia_partido')
        hora_str = cleaned_data.get('hora_inicio_partido') 
        cancha = cleaned_data.get('cancha')

        dia_limite_str = cleaned_data.get('fecha_limite_inscripcion_dia')
        hora_limite_str = cleaned_data.get('fecha_limite_inscripcion_hora')


        equipo_local = cleaned_data.get('equipo_local')
        equipo_visitante = cleaned_data.get('equipo_visitante')

        #logica para que no existan auto-enfrentamientos
        if equipo_local and equipo_visitante and equipo_local == equipo_visitante:
            self.add_error('equipo_visitante', "El equipo visitante no puede ser el mismo que el equipo local.")
        
        if (equipo_local and not equipo_visitante) or (not equipo_local and equipo_visitante):
            self.add_error(None, "Si eliges un equipo permanente, debes seleccionar tanto el local como el visitante, o ninguno para un partido abierto.")


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





class ResultadoPartidoForm(forms.Form):
    goles_local = forms.IntegerField(
        label="Goles del Equipo Local",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': '0'})
    )
    goles_visitante = forms.IntegerField(
        label="Goles del Equipo Visitante",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': '0'})
    )
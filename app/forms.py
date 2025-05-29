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
    # --- Campos para construir la fecha y hora de inicio ---
    dia_partido = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control bg-dark text-white border-secondary',
                # 'min': django_timezone.now().strftime('%Y-%m-%d') # Se valida en clean()
            }
        ),
        label="Día del Partido",
        help_text="Selecciona el día en que se jugará el partido."
    )

    # Generar opciones de hora (de 10:00 a 22:00, en intervalos de 1 hora)
    # Es mejor definir esto fuera del __init__ para que no se regenere cada vez
    HORARIOS_CHOICES = [(time(h, 0).strftime('%H:%M'), f"{h:02d}:00") for h in range(10, 23)]
    # Si quieres añadir "y media":
    # HORARIOS_CHOICES_FULL = []
    # for h in range(10, 23):
    #     HORARIOS_CHOICES_FULL.append((time(h, 0).strftime('%H:%M'), f"{h:02d}:00"))
    #     if h < 22: # Para no tener 22:30 si el último es 22:00
    #         HORARIOS_CHOICES_FULL.append((time(h, 30).strftime('%H:%M'), f"{h:02d}:30"))
    # hora_inicio_partido = forms.ChoiceField(choices=HORARIOS_CHOICES_FULL, ...)


    hora_inicio_partido = forms.ChoiceField(
        choices=HORARIOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Hora de Inicio del Partido"
    )

    # --- Campos para la fecha límite de inscripción (opcionales) ---
    fecha_limite_inscripcion_dia = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control bg-dark text-white border-secondary'}),
        label="Día Límite Inscripción",
        required=False,
        help_text="Opcional. Si no se especifica, será 1 hora antes del partido."
    )
    # Usamos los mismos HORARIOS_CHOICES para la hora límite, añadiendo una opción vacía
    hora_limite_inscripcion_hora = forms.ChoiceField(
        choices=[('', 'HH:MM (Por defecto)')] + HORARIOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Hora Límite Inscripción",
        required=False
    )

    # --- Campos directos del modelo Partido ---
    cancha = forms.ModelChoiceField(
        queryset=Cancha.objects.filter(disponible=True).order_by('nombre_cancha'),
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Cancha",
        empty_label="-- Selecciona una cancha --"
    )
    
    # Asumiendo que NIVEL_CHOICES está definido en el modelo Partido
    nivel = forms.ChoiceField(
        choices=Partido.NIVEL_CHOICES,
        required=False, # Ya que en el modelo es blank=True, null=True
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Nivel Estimado del Partido"
    )

    # Campos para seleccionar equipos permanentes (opcional)
    equipo_local = forms.ModelChoiceField(
        queryset=Equipo.objects.filter(tipo_equipo='PERMANENTE', activo=True),
        required=False,
        label="Equipo Local (Permanente)",
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        help_text="Opcional. Deja en blanco si es un partido abierto o los equipos se forman después.",
        empty_label=" (Ninguno - Partido Abierto)"
    )
    equipo_visitante = forms.ModelChoiceField(
        queryset=Equipo.objects.filter(tipo_equipo='PERMANENTE', activo=True),
        required=False,
        label="Equipo Visitante (Permanente)",
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        help_text="Opcional. Deja en blanco si es un partido abierto o los equipos se forman después.",
        empty_label=" (Ninguno - Partido Abierto)"
    )

    class Meta:
        model = Partido
        fields = [
            # Los campos que el usuario rellena directamente y que son del modelo
            'cancha', 'tipo', 'nivel', 'modalidad',
            'max_jugadores', 'costo', 'metodo_pago', 'comentarios',
            'equipo_local', 'equipo_visitante' # Estos ahora son directos del modelo
        ]
        # 'fecha' y 'fecha_limite_inscripcion' se construirán en clean() y se pasarán a la instancia en la vista.
        # O, si los incluyes en fields, debes asegurarte que el widget no cause conflicto
        # y que el clean() los sobreescriba correctamente.
        # Por simplicidad y control, los construimos en clean() y los asignamos en la vista.

        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'modalidad': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'max_jugadores': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Ej: 10'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': '0.00', 'step': '0.01'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'comentarios': forms.Textarea(attrs={'rows': 3, 'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Reglas especiales, qué llevar, etc.'}),
        }
        labels = {
            'tipo': "Formato del Partido",
            'modalidad': "Modalidad del Partido",
            'max_jugadores': "Máximo de Jugadores Totales",
            'costo': "Costo por Jugador (€)",
            'metodo_pago': "Método de Pago",
            'comentarios': "Comentarios Adicionales",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) # Para filtrar querysets de equipos si es necesario
        super().__init__(*args, **kwargs)

        # Personalizar queryset para equipo_local si se pasa el usuario
        # (para que solo pueda elegir sus equipos, por ejemplo)
        if self.user:
            # Ejemplo: solo equipos donde el usuario es capitán
            # self.fields['equipo_local'].queryset = Equipo.objects.filter(
            #     capitan=self.user, tipo_equipo='PERMANENTE', activo=True
            # ).order_by('nombre_equipo')
            # O todos los equipos permanentes como está definido al declarar el campo
            pass

        # Si estamos editando un partido (self.instance.pk existe)
        if self.instance and self.instance.pk:
            # Pre-rellenar dia_partido y hora_inicio_partido desde self.instance.fecha
            if self.instance.fecha:
                self.fields['dia_partido'].initial = self.instance.fecha.date()
                self.fields['hora_inicio_partido'].initial = self.instance.fecha.strftime('%H:%M')
            
            # Pre-rellenar fecha_limite_inscripcion_dia y _hora
            if self.instance.fecha_limite_inscripcion:
                self.fields['fecha_limite_inscripcion_dia'].initial = self.instance.fecha_limite_inscripcion.date()
                self.fields['fecha_limite_inscripcion_hora'].initial = self.instance.fecha_limite_inscripcion.strftime('%H:%M')
            
            # Los campos equipo_local y equipo_visitante se pre-rellenarán automáticamente
            # por ModelForm si están en Meta.fields.

    def clean(self):
        cleaned_data = super().clean()
        
        dia_partido = cleaned_data.get('dia_partido')
        hora_inicio_str = cleaned_data.get('hora_inicio_partido')
        cancha = cleaned_data.get('cancha')

        fecha_limite_dia = cleaned_data.get('fecha_limite_inscripcion_dia')
        fecha_limite_hora_str = cleaned_data.get('fecha_limite_inscripcion_hora')

        # --- Procesamiento de Fecha de Inicio ---
        if dia_partido and hora_inicio_str:
            try:
                hora_obj = datetime.strptime(hora_inicio_str, '%H:%M').time()
                naive_datetime = datetime.combine(dia_partido, hora_obj)
                fecha_inicio = make_aware(naive_datetime) # Hacerlo aware
                
                if fecha_inicio < django_timezone.now():
                    self.add_error('dia_partido', 'La fecha y hora de inicio no puede ser en el pasado.')
                else:
                    cleaned_data['fecha'] = fecha_inicio # Añadir al cleaned_data para la vista
            except ValueError:
                self.add_error('hora_inicio_partido', "Formato de hora de inicio inválido.")
        elif not dia_partido:
             self.add_error('dia_partido', "Este campo es obligatorio.") # Si no es validado por required=True
        elif not hora_inicio_str:
             self.add_error('hora_inicio_partido', "Este campo es obligatorio.")


        # --- Procesamiento de Fecha Límite de Inscripción ---
        fecha_inicio_calculada = cleaned_data.get('fecha') # Usar la fecha ya procesada y aware

        if fecha_limite_dia and fecha_limite_hora_str:
            try:
                hora_limite_obj = datetime.strptime(fecha_limite_hora_str, '%H:%M').time()
                naive_limite_dt = datetime.combine(fecha_limite_dia, hora_limite_obj)
                fecha_limite_inscripcion_calculada = make_aware(naive_limite_dt)

                if fecha_inicio_calculada and fecha_limite_inscripcion_calculada >= fecha_inicio_calculada:
                    self.add_error('fecha_limite_inscripcion_dia', 'La fecha límite debe ser anterior a la del partido.')
                else:
                    cleaned_data['fecha_limite_inscripcion'] = fecha_limite_inscripcion_calculada
            except ValueError:
                self.add_error('fecha_limite_inscripcion_hora', 'Formato de hora límite inválido.')
        elif fecha_limite_dia or fecha_limite_hora_str: # Si solo uno de los dos está relleno
            self.add_error('fecha_limite_inscripcion_dia', 'Debes especificar día y hora para el límite, o dejar ambos vacíos.')
        else:
            # Si ambos están vacíos, se calculará en el modelo (o aquí si prefieres)
            cleaned_data['fecha_limite_inscripcion'] = None 


        # --- Validación de Solapamiento de Cancha ---
        if fecha_inicio_calculada and cancha:
            fecha_fin_propuesta = fecha_inicio_calculada + timedelta(hours=1)
            
            partidos_conflictivos_query = Partido.objects.filter(
                cancha=cancha,
                estado__in=['PROGRAMADO', 'EN_CURSO'],
                fecha__lt=fecha_fin_propuesta, # Partido existente empieza ANTES de que termine el nuevo
            )
            if self.instance and self.instance.pk:
                partidos_conflictivos_query = partidos_conflictivos_query.exclude(pk=self.instance.pk)

            for partido_existente in partidos_conflictivos_query:
                # Asumiendo que todos los partidos existentes también duran 1 hora
                fin_existente = partido_existente.fecha + timedelta(hours=1) 
                if fin_existente > fecha_inicio_calculada: # Y el existente termina DESPUÉS de que empiece el nuevo
                    self.add_error('hora_inicio_partido', forms.ValidationError(
                        f"La cancha '{cancha.nombre_cancha}' ya está reservada de "
                        f"{partido_existente.fecha.strftime('%H:%M')} a {fin_existente.strftime('%H:%M')} "
                        f"el {partido_existente.fecha.strftime('%d/%m/%Y')}. "
                        f"Intenta con otra hora o cancha.",
                        code='solapamiento'
                    ))
                    # También se podría añadir a 'cancha' o 'dia_partido'
                    # self.add_error('cancha', "Horario no disponible")
                    break 
        
        # --- Validación de Equipos ---
        equipo_local = cleaned_data.get('equipo_local')
        equipo_visitante = cleaned_data.get('equipo_visitante')

        if equipo_local and equipo_visitante and equipo_local == equipo_visitante:
            self.add_error('equipo_visitante', "El equipo visitante no puede ser el mismo que el equipo local.")
        
        # Opcional: si se selecciona un equipo, el otro también debe ser seleccionado
        # if (equipo_local and not equipo_visitante) or (not equipo_local and equipo_visitante):
        #     self.add_error(None, "Si eliges un equipo permanente, debes seleccionar tanto el local como el visitante, o ninguno para un partido abierto.")


        # --- Validación de Costo y Método de Pago ---
        costo = cleaned_data.get("costo")
        metodo_pago = cleaned_data.get("metodo_pago")

        if costo is not None: # Solo validar si costo tiene un valor (no es None)
            if costo > 0 and metodo_pago == 'GRATIS':
                self.add_error('metodo_pago', 'Si el partido tiene un costo, el método de pago no puede ser "Gratis".')
            elif costo == 0 and metodo_pago != 'GRATIS' and metodo_pago: # Si es 0 y se eligió algo que no es gratis
                 cleaned_data['metodo_pago'] = 'GRATIS' # Forzar a gratis o limpiar el método de pago
        elif metodo_pago and metodo_pago != 'GRATIS': # Si costo es None (no se llenó) y se eligió un método de pago no gratis
             self.add_error('costo', 'Debes especificar un costo si el método de pago no es "Gratis".')


        return cleaned_data
    
class AsignarEquiposForm(forms.Form):
    def __init__(self, *args, **kwargs):
        jugadores_inscritos = kwargs.pop('jugadores_inscritos', None)
        partido = kwargs.pop('partido', None)
        super().__init__(*args, **kwargs)

        EQUIPO_CHOICES = [
            ('', 'Sin Asignar'), 
            ('local', 'Equipo Local'),
            ('visitante', 'Equipo Visitante'),
        ]

        if jugadores_inscritos:
            for jugador in jugadores_inscritos:
                initial_assignment = ''
                if partido and partido.equipo_local and jugador in partido.equipo_local.jugadores.all():
                    initial_assignment = 'local'
                elif partido and partido.equipo_visitante and jugador in partido.equipo_visitante.jugadores.all():
                    initial_assignment = 'visitante'
                

                self.fields[f'jugador_{jugador.id}'] = forms.ChoiceField(
                    choices=EQUIPO_CHOICES,
                    required=False,
                    label=jugador.nombre,
                    initial=initial_assignment,
                    widget=forms.Select(attrs={'class': 'form-select form-select-sm mb-1 d-none player-assignment-select', 'data-jugador-id': jugador.id}) 
                )
    

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



#EQUIPOS

class EquipoPermanenteForm(forms.ModelForm):


    class Meta:
        model = Equipo
        fields = [
            'nombre_equipo', 'descripcion', 
            'team_shield', 'team_banner',
        ]
        # 'tipo_equipo' en la vista
        # 'capitan' en la vista
        # 'activo' True por defecto
        widgets = {
            'nombre_equipo': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Nombre de tu equipo'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Una breve descripción del equipo'}),
            'team_shield': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'team_banner': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }
        labels = {
            'nombre_equipo': "Nombre del Equipo",
            'descripcion': "Descripción del Equipo",
            'team_shield': "Escudo del Equipo (Opcional)",
            'team_banner': "Banner del Equipo (Opcional)",
        }

    def clean_nombre_equipo(self):
        nombre = self.cleaned_data.get('nombre_equipo')
        if Equipo.objects.filter(nombre_equipo__iexact=nombre, tipo_equipo='PERMANENTE').exists():
            # Si estamos editando, permitir el mismo nombre si es el mismo equipo
            if not (self.instance and self.instance.pk and self.instance.nombre_equipo == nombre):
                 raise forms.ValidationError("Ya existe un equipo permanente con este nombre.")
        return nombre
        

        
    

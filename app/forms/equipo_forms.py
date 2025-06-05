from django import forms

from app.models.equipo import Equipo
from django.contrib.auth import get_user_model; User = get_user_model()
from django.db.models import Q



class EquipoPermanenteForm(forms.ModelForm):

    miembros_iniciales = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('nombre'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select bg-dark text-white border-secondary', 'size': '5'}),
        required=False,
        label="Añadir Miembros Iniciales (Opcional)",
        help_text="Mantén presionada la tecla Ctrl (o Cmd en Mac) para seleccionar varios."
    )

    class Meta:
        model = Equipo
        fields = [
            'nombre_equipo', 'descripcion', 
            'team_shield', 'team_banner',
        ]
        widgets = {
            'nombre_equipo': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Nombre de tu escuadra'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Lema, historia, objetivos...'}),
            'team_shield': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm bg-dark text-white border-secondary'}),
            'team_banner': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm bg-dark text-white border-secondary'}),
        }
        labels = {
            'nombre_equipo': "Nombre del Equipo",
            'descripcion': "Descripción del Equipo",
            'team_shield': "Escudo del Equipo (Opcional)",
            'team_banner': "Banner del Equipo (Opcional)",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) # usuario actual
        super().__init__(*args, **kwargs)
        
        # se incluye al usuario actual de la lista de miembros iniciales
        if self.user:
            self.fields['miembros_iniciales'].queryset = User.objects.exclude(pk=self.user.pk).order_by('nombre')


    def clean_nombre_equipo(self):
        nombre = self.cleaned_data.get('nombre_equipo')
        query = Equipo.objects.filter(nombre_equipo__iexact=nombre, tipo_equipo='PERMANENTE')
        
        # si se edita excluimos el propio equipo de la comprobación
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
            
        if query.exists():
            raise forms.ValidationError("Ya existe un equipo permanente con este nombre. Por favor, elige otro.")
        return nombre



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
    
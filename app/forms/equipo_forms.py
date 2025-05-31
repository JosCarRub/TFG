from django import forms


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
    
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models.partido import Partido
from django.utils import timezone as django_timezone
from django.db.models import Q 


class MisPartidosView(LoginRequiredMixin, ListView):
    model = Partido # Modelo base, aunque filtraremos mucho
    template_name = 'partidos/mis_partidos.html'
    context_object_name = 'partidos_list' # No lo usaremos directamente, pero ListView lo necesita
    paginate_by = 10 

    def get_queryset(self):
        """
        Este queryset base no se usará directamente para renderizar,
        pero ListView lo necesita. Podemos devolver un queryset vacío
        o uno genérico, ya que la lógica principal estará en get_context_data.
        """
        return Partido.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_actual = self.request.user
        ahora = django_timezone.now()

        # Partidos en los que el usuario está inscrito o es creador
        partidos_del_usuario = Partido.objects.filter(
            Q(jugadores=usuario_actual) | Q(creador=usuario_actual)
        ).distinct().select_related('cancha', 'creador', 'equipo_local', 'equipo_visitante').prefetch_related('jugadores').order_by('fecha')

        # 1. Próximos Partidos Inscritos/Creados
        #    (Estado PROGRAMADO o EN_CURSO y fecha de inicio futura o actual)
        context['proximos_partidos'] = partidos_del_usuario.filter(
            Q(estado='PROGRAMADO') | Q(estado='EN_CURSO'),
            fecha__gte=ahora
        ).order_by('fecha')

        # 2. Partidos Jugados (Historial)
        #    (Estado FINALIZADO o partidos pasados)
        context['partidos_jugados'] = partidos_del_usuario.filter(
            Q(estado='FINALIZADO') | Q(fecha__lt=ahora, estado__in=['PROGRAMADO', 'EN_CURSO', 'CANCELADO'])
            # Incluimos programados/en_curso/cancelados pasados por si acaso
        ).order_by('-fecha') # Los más recientes primero
        
        # Añadir información contextual a cada lista si es necesario (como en BuscarPartidos)
        # Por ejemplo, para 'proximos_partidos':
        proximos_info = []
        for partido in context['proximos_partidos']:
            proximos_info.append({
                'partido': partido,
                'es_creador': (partido.creador == usuario_actual),
                'plazas_disponibles': partido.max_jugadores - partido.jugadores.count(),
                'inscripcion_esta_abierta': partido.inscripcion_abierta
            })
        context['proximos_partidos_info'] = proximos_info

        historial_info = []
        for partido in context['partidos_jugados']:
            historial_info.append({
                'partido': partido,
                'es_creador': (partido.creador == usuario_actual),
                # Para partidos finalizados, mostrar el resultado
                'resultado_str': f"{partido.goles_local or '-'} : {partido.goles_visitante or '-'}" if partido.estado == 'FINALIZADO' else "No finalizado"
            })
        context['partidos_jugados_info'] = historial_info


        context['titulo_pagina'] = "Mis Partidos"
        return context
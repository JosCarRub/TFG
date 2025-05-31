from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from app.models import Partido, User
from django.db.models import Q

# LANDING
class Landing(TemplateView):
    template_name = 'global/landing_page.html'


#HOME
class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_actual = self.request.user
        ahora = timezone.now()

        # 1. Información del Usuario (ya disponible como {{ user }} en el template)
        context['titulo_pagina'] = f"Bienvenido, {usuario_actual.nombre}"

        # 2. Próximos Partidos del Usuario (simplificado, mostrar 2-3)
        proximos_partidos_query = Partido.objects.filter(
            Q(jugadores=usuario_actual) | Q(creador=usuario_actual),
            estado__in=['PROGRAMADO', 'EN_CURSO'],
            fecha__gte=ahora
        ).distinct().select_related('cancha').order_by('fecha')[:3] # Mostrar los próximos 3

        proximos_partidos_info = []
        for partido in proximos_partidos_query:
            proximos_partidos_info.append({
                'partido': partido,
                'es_creador': (partido.creador == usuario_actual),
                'plazas_disponibles': partido.max_jugadores - partido.jugadores.count(),
                'inscripcion_esta_abierta': partido.inscripcion_abierta
            })
        context['proximos_partidos_dashboard'] = proximos_partidos_info
        
        # 3. Actividad Reciente
        ultimo_partido_jugado = Partido.objects.filter(
        Q(jugadores=usuario_actual) | Q(creador=usuario_actual),
        estado='FINALIZADO'
        ).distinct().order_by('-fecha').first()
        context['ultimo_partido_jugado'] = ultimo_partido_jugado



        return context


from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import User, Partido, Equipo, Cancha 
from django.db.models import Count, F, Q, ExpressionWrapper, DateTimeField, IntegerField, FloatField
from django.utils import timezone
from datetime import timedelta

class EstadisticasView(LoginRequiredMixin, TemplateView):
    template_name = 'estadisticas/estadisticas_generales.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Estadísticas de la Comunidad"

        # --- Filtro de Periodo ---
        periodo = self.request.GET.get('periodo', 'todo')
        fecha_desde = None
        now = timezone.now() # Usar el timezone de Django

        if periodo == '7dias':
            fecha_desde = now - timedelta(days=7)
            context['periodo_seleccionado'] = "Últimos 7 días"
        elif periodo == '30dias':
            fecha_desde = now - timedelta(days=30)
            context['periodo_seleccionado'] = "Último mes"
        else:
            periodo = 'todo' # Asegurar que el valor sea consistente para el template
            context['periodo_seleccionado'] = "Todo el tiempo"
        
        context['periodo_actual_param'] = periodo

        # --- 1. Jugadores con más Puntuación ELO (Top 10) ---
        context['top_elo_jugadores'] = User.objects.filter(
            is_active=True
        ).order_by('-calificacion')[:10]

        # --- 2. Jugadores más Activos (más partidos jugados en el periodo) (Top 10) ---
        # Usaremos el related_name 'get_jugadores_partido' de Partido.jugadores
        jugadores_activos_query = User.objects.filter(is_active=True)
        
        if fecha_desde:
            jugadores_activos_query = jugadores_activos_query.annotate(
                num_partidos_periodo=Count(
                    'get_jugadores_partido', # related_name desde User a Partido via Partido.jugadores
                    filter=Q(get_jugadores_partido__estado='FINALIZADO', get_jugadores_partido__fecha__gte=fecha_desde)
                )
            ).filter(num_partidos_periodo__gt=0).order_by('-num_partidos_periodo', '-calificacion')[:10]
        else: # Todo el tiempo
            # Usamos el campo 'partidos_jugados' del modelo User, que se actualiza en registrar_resultado_y_actualizar_stats
            jugadores_activos_query = jugadores_activos_query.filter(
                partidos_jugados__gt=0
            ).order_by('-partidos_jugados', '-calificacion')[:10]
        
        context['top_jugadores_activos'] = jugadores_activos_query


        # --- 3. Equipos Permanentes con más Partidos y Victorias (Top 10) ---
        # Usaremos los campos 'partidos_jugados_permanente' y 'victorias_permanente' si el periodo es 'todo'.
        # Para periodos filtrados, calcularemos dinámicamente.
        equipos_query = Equipo.objects.filter(tipo_equipo='PERMANENTE', activo=True)
        
        # Para pasar al template y decidir qué campos mostrar
        context['equipo_usa_stats_precalculadas_para_periodo_todo'] = hasattr(Equipo, 'partidos_jugados_permanente')

        if fecha_desde:
            equipos_query = equipos_query.annotate(
                partidos_jugados_periodo_local=Count(
                    'get_equipo_local', # related_name de Partido.equipo_local
                    filter=Q(get_equipo_local__estado='FINALIZADO', get_equipo_local__fecha__gte=fecha_desde)
                ),
                partidos_jugados_periodo_visitante=Count(
                    'get_equipo_visitante', # related_name de Partido.equipo_visitante
                    filter=Q(get_equipo_visitante__estado='FINALIZADO', get_equipo_visitante__fecha__gte=fecha_desde)
                ),
                victorias_periodo_local=Count(
                    'get_equipo_local', 
                    filter=Q(get_equipo_local__estado='FINALIZADO', 
                             get_equipo_local__fecha__gte=fecha_desde, 
                             get_equipo_local__goles_local__gt=F('get_equipo_local__goles_visitante'))
                ),
                victorias_periodo_visitante=Count(
                    'get_equipo_visitante', 
                    filter=Q(get_equipo_visitante__estado='FINALIZADO', 
                             get_equipo_visitante__fecha__gte=fecha_desde, 
                             get_equipo_visitante__goles_visitante__gt=F('get_equipo_visitante__goles_local'))
                )
            ).annotate(
                # Sumar los conteos para obtener el total del periodo
                partidos_jugados_periodo=ExpressionWrapper(F('partidos_jugados_periodo_local') + F('partidos_jugados_periodo_visitante'), output_field=IntegerField()),
                victorias_periodo=ExpressionWrapper(F('victorias_periodo_local') + F('victorias_periodo_visitante'), output_field=IntegerField())
            ).filter(partidos_jugados_periodo__gt=0).order_by('-victorias_periodo', '-partidos_jugados_periodo')[:10]
        else: # Todo el tiempo
            if hasattr(Equipo, 'partidos_jugados_permanente') and hasattr(Equipo, 'victorias_permanente'):
                print("DEBUG: Usando campos precalculados para Equipos (Todo el tiempo)")
                equipos_query = equipos_query.filter(partidos_jugados_permanente__gt=0).order_by('-victorias_permanente', '-partidos_jugados_permanente')[:10]
            else: # Fallback si no tienes los campos precalculados
                equipos_query = equipos_query.annotate(
                    num_partidos_local=Count('get_equipo_local', filter=Q(get_equipo_local__estado='FINALIZADO')),
                    num_partidos_visitante=Count('get_equipo_visitante', filter=Q(get_equipo_visitante__estado='FINALIZADO')),
                    num_victorias_local=Count('get_equipo_local', filter=Q(get_equipo_local__estado='FINALIZADO', get_equipo_local__goles_local__gt=F('get_equipo_local__goles_visitante'))),
                    num_victorias_visitante=Count('get_equipo_visitante', filter=Q(get_equipo_visitante__estado='FINALIZADO', get_equipo_visitante__goles_visitante__gt=F('get_equipo_visitante__goles_local')))
                ).annotate(
                    num_partidos=ExpressionWrapper(F('num_partidos_local') + F('num_partidos_visitante'), output_field=IntegerField()),
                    num_victorias=ExpressionWrapper(F('num_victorias_local') + F('num_victorias_visitante'), output_field=IntegerField())
                ).filter(num_partidos__gt=0).order_by('-num_victorias', '-num_partidos')[:10]

        context['top_equipos_activos'] = equipos_query

        # --- 4. Canchas más Populares (más partidos jugados en el periodo) (Top 10) ---
        # related_name de Partido.cancha es 'get_cancha_partido'
        canchas_query = Cancha.objects.filter(disponible=True)
        if fecha_desde:
            canchas_query = canchas_query.annotate(
                num_partidos_cancha=Count(
                    'get_cancha_partido', 
                    filter=Q(get_cancha_partido__estado='FINALIZADO', get_cancha_partido__fecha__gte=fecha_desde)
                )
            ).filter(num_partidos_cancha__gt=0).order_by('-num_partidos_cancha')[:10]
        else: # Todo el tiempo
            canchas_query = canchas_query.annotate(
                num_partidos_cancha=Count(
                    'get_cancha_partido',
                    filter=Q(get_cancha_partido__estado='FINALIZADO')
                )
            ).filter(num_partidos_cancha__gt=0).order_by('-num_partidos_cancha')[:10]
            
        context['top_canchas_populares'] = canchas_query

        return context
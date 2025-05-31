from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

from app.models.historial import HistorialELO
from app.models.user import User




class Partido(models.Model):
    TIPO_CHOICES = [
        ('SALA', 'Fútbol Sala'),
        ('F7', 'Fútbol 7'),
        ('F11', 'Fútbol 11'),
    ]
    
    MODALIDAD_CHOICES = [
        ('AMISTOSO', 'Amistoso'),
        ('COMPETITIVO', 'Competitivo'),
    ]
    
    NIVEL_CHOICES = [ 
        ('', 'Cualquier nivel'),
        ('PRINCIPIANTE', 'Principiante'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
        ('PRO', 'Profesional/Muy Alto'),
    ]

    ESTADO_CHOICES = [
        ('PROGRAMADO', 'Programado'),
        ('EN_CURSO', 'En curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('Bizum', 'Bizum'),
        ('GRATIS', 'Gratuito'),
    ]

    id_partido = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateTimeField(verbose_name="Fecha y Hora de Inicio")
    fecha_limite_inscripcion = models.DateTimeField(
        verbose_name="Fecha Límite de Inscripción",
        blank=True, null=True,
        help_text="Hasta cuándo se pueden inscribir los jugadores. Si se deja en blanco, se calculará una hora antes del partido."
    )

    cancha = models.ForeignKey("app.Cancha", on_delete=models.CASCADE, related_name='get_cancha_partido')
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES)
    nivel = models.CharField(max_length=50, choices=NIVEL_CHOICES, blank=True, null=True)
    modalidad = models.CharField(max_length=11, choices=MODALIDAD_CHOICES, blank=True, null=True)
    max_jugadores = models.PositiveIntegerField(validators=[MinValueValidator(2)])
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    metodo_pago = models.CharField(max_length=13, choices=METODO_PAGO_CHOICES, blank=True, null=True)
    creador = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name='get_user_creador')
    jugadores = models.ManyToManyField("app.User", related_name='get_jugadores_partido', blank=True)
    equipo_local = models.ForeignKey("app.Equipo", on_delete=models.SET_NULL, null=True, blank=True, related_name='get_equipo_local')
    equipo_visitante = models.ForeignKey("app.Equipo", on_delete=models.SET_NULL, null=True, blank=True, related_name='get_equipo_visitante')
    goles_local = models.PositiveIntegerField(null=True, blank=True)
    goles_visitante = models.PositiveIntegerField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PROGRAMADO')
    calificacion_actualizada = models.BooleanField(default=False)
    comentarios = models.TextField(blank=True, null=True)

    @property
    def fecha_fin_calculada(self): # Propiedad para calcular la hora de finalización (1 hora después)
        if self.fecha:
            return self.fecha + timedelta(hours=1)
        return None
    
    @property
    def inscripcion_abierta(self): #Determina si la inscripción al partido sigue abierta.
        
        ahora = timezone.now()
        limite = self.fecha_limite_inscripcion_efectiva
        return self.estado == 'PROGRAMADO' and ahora < limite and self.jugadores.count() < self.max_jugadores
    
    @property
    def fecha_limite_inscripcion_efectiva(self): #Devuelve la fecha límite de inscripción, calculándola si no está definida.
        
        if self.fecha_limite_inscripcion:
            return self.fecha_limite_inscripcion
        if self.fecha:
            return self.fecha - timedelta(hours=1) # Por defecto, 1 hora antes del partido
        return None
    
    def save(self, *args, **kwargs): # Calcular fecha_limite_inscripcion por defecto si no se provee

        if not self.fecha_limite_inscripcion and self.fecha:
            self.fecha_limite_inscripcion = self.fecha - timedelta(hours=1)
        super().save(*args, **kwargs)


    def actualizar_calificaciones(self):
        if self.calificacion_actualizada or self.modalidad == 'AMISTOSO':
            return

        if not self.equipo_local or not self.equipo_visitante:
            return  

        if self.goles_local is None or self.goles_visitante is None:
            return

        K = 32  # Constante de sensibilidad ELO

        rating_local = self.equipo_local.calificacion_promedio()
        rating_visitante = self.equipo_visitante.calificacion_promedio()

        if self.goles_local > self.goles_visitante:
            score_local = 1
        elif self.goles_local < self.goles_visitante:
            score_local = 0
        else:
            score_local = 0.5

        score_visitante = 1 - score_local

        expected_local = 1 / (1 + 10 ** ((rating_visitante - rating_local) / 400))
        expected_visitante = 1 - expected_local

        for jugador in self.equipo_local.jugadores.all():
            calificacion_antes = jugador.calificacion
            jugador.calificacion += K * (score_local - expected_local)
            jugador.save()

            HistorialELO.objects.create(
                user=jugador,
                partido=self,
                calificacion_antes=calificacion_antes,
                calificacion_despues=jugador.calificacion
            )

        for jugador in self.equipo_visitante.jugadores.all():
            calificacion_antes = jugador.calificacion
            jugador.calificacion += K * (score_visitante - expected_visitante)
            jugador.save()

            HistorialELO.objects.create(
                user=jugador,
                partido=self,
                calificacion_antes=calificacion_antes,
                calificacion_despues=jugador.calificacion
            )

        self.calificacion_actualizada = True
        self.save(update_fields=['calificacion_actualizada'])

    def registrar_resultado_y_actualizar_stats(self, goles_local, goles_visitante):
        if self.estado == 'FINALIZADO':
        # Podrías permitir actualizar un resultado, pero cuidado con recalcular ELO y stats
        # messages.info(request, "El resultado de este partido ya fue registrado.")
        # return
            pass

        self.goles_local = goles_local
        self.goles_visitante = goles_visitante
        self.estado = 'FINALIZADO'
    
    # Actualizar estadísticas de equipos permanentes
        if self.equipo_local and self.equipo_local.tipo_equipo == 'PERMANENTE':
            self.equipo_local.partidos_jugados_permanente += 1
            if self.goles_local > self.goles_visitante:
                self.equipo_local.victorias_permanente += 1

            self.equipo_local.save()

        if self.equipo_visitante and self.equipo_visitante.tipo_equipo == 'PERMANENTE':
            self.equipo_visitante.partidos_jugados_permanente += 1
            if self.goles_visitante > self.goles_local:
                self.equipo_visitante.victorias_permanente += 1
            self.equipo_visitante.save()

    
    
    # Por ejemplo:
        jugadores_del_partido = list(self.equipo_local.jugadores.all()) + list(self.equipo_visitante.jugadores.all()) if self.equipo_local and self.equipo_visitante else list(self.jugadores.all())
    
        for jugador_obj in User.objects.filter(pk__in=[j.pk for j in set(jugadores_del_partido)]): # set() para evitar duplicados
            jugador_obj.partidos_jugados +=1
            if self.equipo_local and jugador_obj in self.equipo_local.jugadores.all():
                if self.goles_local > self.goles_visitante:
                    jugador_obj.victorias +=1
                elif self.goles_local == self.goles_visitante:
                    jugador_obj.empates +=1
                else:
                    jugador_obj.derrotas +=1
            elif self.equipo_visitante and jugador_obj in self.equipo_visitante.jugadores.all():
                if self.goles_visitante > self.goles_local:
                    jugador_obj.victorias +=1
                elif self.goles_local == self.goles_visitante:
                    jugador_obj.empates +=1
                else:
                    jugador_obj.derrotas +=1
            jugador_obj.save()


        self.save() # Guardar el partido con resultado y estado
    
    # Llamar a la actualización de ELO si no es amistoso
        if self.modalidad != 'AMISTOSO':
            self.actualizar_calificaciones()



    def __str__(self):
        hora_inicio_str = self.fecha.strftime('%d/%m/%Y %H:%M') if self.fecha else "Fecha no definida"
        hora_fin_str = self.fecha_fin_calculada.strftime('%H:%M') if self.fecha_fin_calculada else ""
        nombre_cancha_str = self.cancha.nombre_cancha if self.cancha else "Cancha no definida"
        
        return f"Partido en {nombre_cancha_str} - {hora_inicio_str} a {hora_fin_str}"
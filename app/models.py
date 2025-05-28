from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid


from django.db import models


#EXPLICAR JI EL PORQUÉ DE LOS ID, ASÍ SE PUEDE 'ENGAÑAR AL USUARIO'

class User(AbstractUser):
    TIPO_GENERO = [
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
        ('NO_ESPECIFICADO', 'Prefiero no decirlo'),
        ('OTRO', 'Otro'),
    ]

    TIPO_POSICION = [
        ('DELANTERO', 'Delantero'),
        ('CENTROCAMPISTA', 'Centrocampista'),
        ('DEFENSA', 'Defensa'),
        ('PORTERO', 'Portero')
    ]

    username = models.EmailField(max_length=150, unique=True, verbose_name="email", help_text="Introduce un email válido",)
    nombre = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    genero = models.CharField(max_length=20, choices=TIPO_GENERO, default='NO_ESPECIFICADO', blank=True, null=True)
    
    posicion = models.CharField(max_length=50,choices=TIPO_POSICION, blank=True, null=True)
    partidos_jugados = models.IntegerField(default=0)
    victorias = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
     
    calificacion = models.FloatField(default=1000.0)  # ELO

    imagen_perfil = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    banner_perfil = models.ImageField(upload_to='banner_perfil/', blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    #HAY QUE MANEJAR LA FOTO DE PERFIL Y BANNER POR DEFECTO Y SI NO LA PONE
    #QUE SE PONGA UNA SEGUN EL NIVEL QUE TENGA DE UN JUGADOR U OTRO


    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        #CASO DE QUE USUARIO CAMBIE DE EMAIL POR PERDIDA DE CONTRASEÑA
        if self.pk:  # Si ya es un usuario existente
            originalUser = User.objects.get(pk=self.pk)
            if originalUser.email != self.email:  # si cambia el email
                self.username = self.email  # actualizo el username

        super().save(*args, **kwargs)


class Cancha(models.Model):
    TIPO_CHOICES = [
        ('SALA', 'Fútbol Sala'),
        ('F7', 'Fútbol 7'),
        ('F11', 'Fútbol 11'),
    ]
    
    PROPIEDAD_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('PRIVADA', 'Privada'),
    ]

    SUPERFICIE_CHOICES = [
        ('FUTBOL SALA','Fútbol sala'),
        ('CESPED ARTIFICIAL','Césped artificial'),
        ('CESPED NATURAL','Césped natural'),
        ('TIERRA','Tierra'),
        ('CEMENTO','Cemento')
    ]
    
    id_cancha = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_cancha = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255)
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES)
    superficie = models.CharField(max_length=50,choices=SUPERFICIE_CHOICES)
    propiedad = models.CharField(max_length=7, choices=PROPIEDAD_CHOICES)
    costo_partido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    disponible = models.BooleanField(default=True, null=True, blank=True)
    imagen = models.ImageField(upload_to='images/canchas_pictures/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre_cancha} - {self.get_tipo_display()}"
    

class Equipo(models.Model):

    TIPO_EQUIPO_CHOICES = [
        ('PARTIDO', 'Equipo para un partido'),
        ('TORNEO', 'Equipo para torneo'),
        ('PERMANENTE', 'Equipo permanente'),
    ]
    
    id_equipo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_equipo = models.CharField(max_length=100)
    capitan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='get_user_captain')
    jugadores = models.ManyToManyField(User, related_name='equipos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True)
    team_shield = models.ImageField(upload_to='team_shield/', null=True, blank=True)
    team_banner = models.ImageField(upload_to='banner_perfil/', blank=True, null=True)
    tipo_equipo = models.CharField(max_length=10, choices=TIPO_EQUIPO_CHOICES)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    def calificacion_promedio(self):
        jugadores = self.jugadores.all()
        if not jugadores.exists():
            return 1000.0
        return sum(j.calificacion for j in jugadores) / jugadores.count() 

class Torneo(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_CURSO', 'En curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPO_CHOICES = [
        ('SALA', 'Fútbol Sala'),
        ('F7', 'Fútbol 7'),
        ('F11', 'Fútbol 11'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_torneo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    equipos = models.ManyToManyField(Equipo, related_name='torneos')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES)
    costo_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    premio = models.CharField(max_length=255, blank=True)
    num_max_equipos = models.PositiveIntegerField(default=8)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"

class Partido(models.Model):
    TIPO_CHOICES = [
        ('SALA', 'Fútbol Sala'),
        ('F7', 'Fútbol 7'),
        ('F11', 'Fútbol 11'),
    ]
    
    MODALIDAD_CHOICES = [
        ('AMISTOSO', 'Amistoso'),
        ('COMPETITIVO', 'Competitivo'),
        ('TORNEO', 'Partido de Torneo'),
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

    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name='get_cancha_partido')
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES)
    nivel = models.CharField(max_length=50, choices=NIVEL_CHOICES, blank=True, null=True)
    modalidad = models.CharField(max_length=11, choices=MODALIDAD_CHOICES, blank=True, null=True)
    max_jugadores = models.PositiveIntegerField(validators=[MinValueValidator(2)])
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    metodo_pago = models.CharField(max_length=13, choices=METODO_PAGO_CHOICES, blank=True, null=True)
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='get_user_creador')
    jugadores = models.ManyToManyField(User, related_name='partidos', blank=True)
    equipo_local = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True, related_name='get_equipo_local')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True, related_name='get_equipo_visitante')
    goles_local = models.PositiveIntegerField(null=True, blank=True)
    goles_visitante = models.PositiveIntegerField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PROGRAMADO')
    torneo = models.ForeignKey(Torneo, on_delete=models.SET_NULL, null=True, blank=True, related_name='get_torneo_partido')
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



    def __str__(self):
        hora_inicio_str = self.fecha.strftime('%d/%m/%Y %H:%M') if self.fecha else "Fecha no definida"
        hora_fin_str = self.fecha_fin_calculada.strftime('%H:%M') if self.fecha_fin_calculada else ""
        nombre_cancha_str = self.cancha.nombre_cancha if self.cancha else "Cancha no definida"
        
        return f"Partido en {nombre_cancha_str} - {hora_inicio_str} a {hora_fin_str}"
    
    def __str__(self):
        if self.equipo_local and self.equipo_visitante:
            return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
        return f"Partido en {self.cancha.nombre} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class Resultado(models.Model):
    partido = models.OneToOneField(Partido, on_delete=models.CASCADE, related_name='get_partido_resultado')
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resultado: {self.partido}"

class Inscripcion(models.Model):
    TIPO_CHOICES = [
        ('JUGADOR_PARTIDO', 'Jugador a Partido'),
        ('EQUIPO_TORNEO', 'Equipo a Torneo'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    # Para inscripciones de jugadores a partidos
    jugador = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='get_jugador_inscripcion')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, null=True, blank=True, related_name='get_partido_inscripcion')
    
    # Para inscripciones de equipos a torneos
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, blank=True, related_name='get_equipo_inscripcionTorneo')
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, null=True, blank=True, related_name='get_jugador_inscripcionTorneo')
    
    pago_confirmado = models.BooleanField(default=False)
    comentarios = models.TextField(blank=True)
    
    def __str__(self):
        if self.tipo == 'JUGADOR_PARTIDO':
            return f"{self.jugador.username} - {self.partido}"
        return f"{self.equipo.nombre} - {self.torneo.nombre}"

class HistorialELO(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='get_user_historialElo')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='get_partido_historialElo')
    calificacion_antes = models.FloatField()
    calificacion_despues = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.nombre} ({self.fecha.strftime('%d/%m/%Y')}) - {self.calificacion_antes} → {self.calificacion_despues}"
import uuid
from django.db import models

from app.models.user import User


class Equipo(models.Model):

    TIPO_EQUIPO_CHOICES = [
        ('PARTIDO', 'Equipo para un partido'),
        ('PERMANENTE', 'Equipo permanente'),
    ]
    
    id_equipo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_equipo = models.CharField(max_length=100)
    capitan = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name='get_user_captain_equipo')
    jugadores = models.ManyToManyField("app.User", related_name='get_jugadores_equipo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True) 
    team_shield = models.ImageField(upload_to='images/team_shields/', null=True, blank=True) 
    team_banner = models.ImageField(upload_to='images/team_banners/', null=True, blank=True) 
    tipo_equipo = models.CharField(max_length=10, choices=TIPO_EQUIPO_CHOICES)
    activo = models.BooleanField(default=True)

    partidos_jugados_permanente = models.PositiveIntegerField(default=0)
    victorias_permanente = models.PositiveIntegerField(default=0)

    partido_asociado = models.ForeignKey("app.Partido", on_delete=models.CASCADE, null=True, blank=True, related_name='get_partido_equipos')
    
    def __str__(self):
        return self.nombre_equipo
    
    def calificacion_promedio(self):
        jugadores = self.jugadores.all()
        if not jugadores.exists():
            return 1000.0
        return sum(j.calificacion for j in jugadores) / jugadores.count()
    
    def clean(self):
        super().clean()
        if self.tipo_equipo == 'PARTIDO' and not self.partido_asociado:
            # Un equipo de tipo PARTIDO debería siempre tener un partido_asociado.
            pass 
        if self.tipo_equipo == 'PERMANENTE' and self.partido_asociado:

            self.partido_asociado = None 

    def save(self, *args, **kwargs):
        if self.tipo_equipo == 'PERMANENTE':
            self.partido_asociado = None
        super().save(*args, **kwargs)
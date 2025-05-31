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
    jugadores = models.ManyToManyField("app.User", related_name='equipos')
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
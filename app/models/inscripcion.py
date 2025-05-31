import uuid
from django.db import models



class Inscripcion(models.Model):
    TIPO_CHOICES = [
        ('JUGADOR_PARTIDO', 'Jugador a Partido'),
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
    jugador = models.ForeignKey("app.User", on_delete=models.CASCADE, null=True, blank=True, related_name='get_jugador_inscripcion')
    partido = models.ForeignKey("app.Partido", on_delete=models.CASCADE, null=True, blank=True, related_name='get_partido_inscripcion')
    
    
    pago_confirmado = models.BooleanField(default=False)
    comentarios = models.TextField(blank=True)
    
    def __str__(self):
        if self.tipo == 'JUGADOR_PARTIDO':
            return f"{self.jugador.username} - {self.partido}"
        return f"{self.equipo.nombre} - {self.torneo.nombre}"
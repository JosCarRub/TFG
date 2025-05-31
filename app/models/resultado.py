from django.db import models

class Resultado(models.Model):
    partido = models.OneToOneField('app.Partido', on_delete=models.CASCADE, related_name='get_partido_resultado')
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resultado: {self.partido}"
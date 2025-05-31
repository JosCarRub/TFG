from django.db import models



class HistorialELO(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name='get_user_historialElo')
    partido = models.ForeignKey('app.Partido', on_delete=models.CASCADE)  
    calificacion_antes = models.FloatField()
    calificacion_despues = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.nombre} ({self.fecha.strftime('%d/%m/%Y')}) - {self.calificacion_antes} → {self.calificacion_despues}"
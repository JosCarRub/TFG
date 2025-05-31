import uuid
from django.db import models

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
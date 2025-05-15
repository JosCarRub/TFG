from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.


admin.site.register(Equipo)
admin.site.register(Partido)
admin.site.register(Cancha)
admin.site.register(Resultado)
admin.site.register(Inscripcion)
admin.site.register(HistorialELO)


class MyAdmin(UserAdmin):
    model = User

    list_display = ("email", "username", "nombre", "calificacion", "posicion")
    search_fields = ("email", "nombre", "posicion")

    ordering = ("-calificacion",)

    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {
            "fields": (
                "nombre", "fecha_nacimiento", "genero", "posicion",
                "ubicacion", "imagen_perfil"
            )
        }),
        ('📊 Estadísticas', {
            "fields": (
                "partidos_jugados", "victorias", "derrotas", "empates", "calificacion"
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            "fields": (
                "nombre", "fecha_nacimiento", "genero", "posicion",
                "ubicacion", "imagen_perfil"
            )
        }),
        ('📊 Estadísticas', {
            "fields": (
                "partidos_jugados", "victorias", "derrotas", "empates", "calificacion"
            )
        }),
    )



# Registra el Admin
admin.site.register(User, MyAdmin)
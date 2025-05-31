from django import forms
from app.models.cancha import Cancha



class CanchasForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre_cancha', 'ubicacion', 'tipo', 'propiedad', 'superficie',
                 'costo_partido', 'descripcion', 'disponible', 'imagen']
        
        def __init__(self, *args, **kwargs):
            super(CanchasForm, self).__init__(*args, **kwargs)
        
            # Nombres personalizados para los campos
            self.fields['nombre_cancha'].label = "Nombre de la cancha"
            self.fields['ubicacion'].label = "Dirección completa"
            self.fields['tipo'].label = "Formato de la cancha (Ej: Fútbol 7)"
            self.fields['propiedad'].label = "Tipo de propiedad"
            self.fields['superficie'].label = "Superficie de juego"
            self.fields['costo_partido'].label = "Costo del Alquiler/Partido (€) (Dejar en 0 o vacío si es gratis)"
            self.fields['descripcion'].label = "Descripción Adicional"
            self.fields['disponible'].label = "Disponible para reservas generales"
            self.fields['imagen'].label = "Foto de la cancha (opcional)"
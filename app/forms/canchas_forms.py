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
            self.fields['tipo'].label = "Tipo de cancha"
            self.fields['propiedad'].label = "Tipo de propiedad"
            self.fields['costo_por_hora'].label = "Precio por hora"
            self.fields['descripcion'].label = "Descripción"
            self.fields['disponible'].label = "Disponible para reservas"
            self.fields['imagen'].label = "Imagen de la cancha"
from .canchas_views import CanchasView, RegistrarCanchaView, DetalleCanchaView
from .commons_views import Landing, Home, Estadisticas
from .partido_views import CrearPartidos, BuscarPartidos,DetallePartidoView, InscribirsePartidoView, RegistrarResultadoPartidoView
from .user_views import UserRegister,Perfil, UserUpdateProfile
from .equipo_views import CrearEquipoPermanenteView, MisEquiposListView, DetalleEquipoView, EditarEquipoPermanenteView


__all__ = [
    "CanchasView",
    "RegistrarCanchaView",
    "DetalleCanchaView",
    "Landing",
    "Home",
    "Estadisticas",
    "CrearPartidos",
    "BuscarPartidos",
    "DetallePartidoView",
    "InscribirsePartidoView",
    "RegistrarResultadoPartidoView",
    "UserRegister",
    "Perfil",
    "UserUpdateProfile",
    "CrearEquipoPermanenteView",
    "MisEquiposListView",
    "DetalleEquipoView",
    "EditarEquipoPermanenteView",
]

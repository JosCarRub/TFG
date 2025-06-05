from .canchas_views import CanchasView, RegistrarCanchaView, DetalleCanchaView
from .commons_views import Landing, Home, DashboardAdmin, DashboardAdminVoice
from .partido_views import CrearPartidos, BuscarPartidos,DetallePartidoView, InscribirsePartidoView, RegistrarResultadoPartidoView
from .user_views import UserRegister,Perfil, UserUpdateProfile
from .equipo_views import CrearEquipoPermanenteView, MisEquiposListView, DetalleEquipoView, EditarEquipoPermanenteView
from .estadisticas_views import EstadisticasView
from .mis_partidos_views import MisPartidosView


__all__ = [
    "CanchasView",
    "RegistrarCanchaView",
    "DetalleCanchaView",
    "Landing",
    "Home",
    "DashboardAdmin",
    "DashboardAdminVoice",
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
    "MisPartidosView",
    "EstadisticasView"
]

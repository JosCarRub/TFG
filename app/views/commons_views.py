from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


# LANDING
class Landing(TemplateView):
    template_name = 'landing.html'


#HOME
class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

class Estadisticas(LoginRequiredMixin, TemplateView):
    template_name = 'estadisticas.html'
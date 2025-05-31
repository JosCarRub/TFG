from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView,CreateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from app.forms.user_forms import UserRegisterForm, UserUpdateProfilelForm
from app.models.user import User


#REGISTRO
class UserRegister(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        
        return super().form_valid(form)
    
    


#PERFIL
class Perfil(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'perfil/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class UserUpdateProfile(LoginRequiredMixin, UpdateView):

    model = User
    form_class = UserUpdateProfilelForm
    template_name = 'perfil/update_profile.html'
    success_url = reverse_lazy('perfil')

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):

        messages.success(self.request, '¡Tu perfil ha sido actualizado con éxito!')

        return super().form_valid(form)
    
    def form_invalid(self, form):

        messages.error(self.request, 'No ha sido posible actuliazar tu perfil, revisa los campos que has querido actulizar por que debe haber un error.')

        return super().form_invalid(form)

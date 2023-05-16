from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from django.views import generic


class SignupView(generic.CreateView):
    template_name = 'signup.html'
    success_url = reverse_lazy('home')
    form_class = CustomUserCreationForm
    success_message = "Account created successfully"

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user is not None:
            login(self.request, user)
        return response


class HomeView(generic.TemplateView):
    template_name = 'home.html'

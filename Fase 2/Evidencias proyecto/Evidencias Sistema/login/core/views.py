from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from .forms import *
from django.contrib.auth import authenticate, login
from .models import *


# Create your views here.

def home(request):
    return render(request, 'core/home.html')



def campanas(request):
    campanas = Campana.objects.all()
    data = {
        'campanas': campanas
    }
    return render(request, 'core/campanas.html', data)


def exit(request):
    logout(request)
    return redirect('home')


def register(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)

        if user_creation_form.is_valid():
            user_creation_form.save()
            
            user = authenticate(username=user_creation_form.cleaned_data['username'], password=user_creation_form.cleaned_data['password1'])
            login(request,user)

            return redirect('home')

    return render(request, 'registration/register.html', data)


def agregar_campana(request):
    if request.method == 'POST':
        form = CampanaForm(request.POST, request.FILES)
        if form.is_valid():
            campana = form.save(commit=False)  # No guarda aún en la base de datos
            campana.user = request.user        # Asigna el usuario autenticado
            campana.save()                     # Guarda en la base de datos
            return redirect('campanas')  # Redirige después de guardar
    else:
        form = CampanaForm()
    
    data = {
        'form': form
    }
    return render(request, 'core/campana/agregar.html', data)

def listar_campanas(request):
    campana = Campana.objects.filter(user=request.user)
    data = {
        'campana': campana
    }
    return render (request, 'core/campana/listar.html', data)


def modificar_campana(request, id):

    campana = get_object_or_404(Campana, id=id)

    data = {
        'form': CampanaForm(instance=campana)
    }

    if request.method == 'POST':
        formulario = CampanaForm(data=request.POST, instance=campana, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listar_campana")
        data["form"] = formulario

    return render(request, 'core/campana/modificar.html', data)


def eliminar_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    campana.delete()
    return redirect(to="listar_campana")
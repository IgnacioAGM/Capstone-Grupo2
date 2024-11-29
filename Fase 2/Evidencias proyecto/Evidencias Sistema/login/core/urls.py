"""
URL configuration for login project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('campanas/', campanas, name='campanas'),
    path('logout/', exit, name='exit'),
    path('register/', register, name='register'),
    path('agregar-campana/', agregar_campana, name='agregar_campana'),
    path('listar-campana/', listar_campanas, name='listar_campana'),
    path('modificar-campana/<uuid:uuid>/', modificar_campana, name='modificar_campana'),
    path('eliminar-campana/<id>/', eliminar_campana, name='eliminar_campana'),
    path('moderar-campanas/', moderar_campanas, name='moderar_campanas'),
    path('aprobar-campana/<int:pk>/', aprobar_campana, name='aprobar_campana'),
    path('rechazar-campana/<int:pk>/', rechazar_campana, name='rechazar_campana'),
    path('donacion/<int:campana_id>/', iniciar_donacion, name='iniciar_donacion'),
    path('donacion/confirmar/', confirmar_donacion, name='confirmar_donacion'),
    path('error/', error, name='error'),
    path('historial-donaciones/', historial_donaciones, name='historial_donaciones'),
    path('detalle-campana/<int:id>/', detalle_campana, name='detalle_campana'),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', custom_password_reset_confirm, name='password_reset_confirm'),
]


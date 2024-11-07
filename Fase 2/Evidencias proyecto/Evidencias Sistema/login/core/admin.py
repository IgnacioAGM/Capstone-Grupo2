from django.contrib import admin

from django.contrib import admin
from .models import (
    TipoCampana, Campana,
    Publicidad, Region, Comuna, Donador, Transaccion, Donacion
)

# Registra cada modelo en el administrador
admin.site.register(TipoCampana)
admin.site.register(Campana)
admin.site.register(Publicidad)
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(Donador)
admin.site.register(Transaccion)
admin.site.register(Donacion)


# Register your models here.

# Register your models here.

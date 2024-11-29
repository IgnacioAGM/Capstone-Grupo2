from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import User
import uuid

# Modelo TipoCampana
class TipoCampana(models.Model):
    nombre_tipo_campana = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_tipo_campana


# Modelo Campana
class Campana(models.Model):
    estados = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),]
    nombre_campana = models.CharField(max_length=200)
    descripcion_campana = models.TextField()
    monto_objetivo_campana = models.IntegerField()
    fecha_fin_campana = models.DateField()
    fecha_inicio_campana = models.DateField()
    link_webpay = models.URLField(max_length=500)
    imagen_campana = models.ImageField(upload_to="imagenes_campana", null=True, blank=True)
    tipo_campana = models.ForeignKey(TipoCampana, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=estados, default='Pendiente')
    monto_donado = models.IntegerField(default=0)  # Campo para almacenar el monto total donado
    slug = models.SlugField(unique=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre_campana)
        super().save(*args, **kwargs)

# Modelo Publicidad
class Publicidad(models.Model):
    nombre_publicidad = models.CharField(max_length=100)
    descripcion_publicidad = models.TextField()
    precio_publicidad = models.IntegerField()
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_publicidad

# Modelo Region
class Region(models.Model):
    nombre_region = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_region

# Modelo Comuna
class Comuna(models.Model):
    nombre_comuna = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_comuna

# Modelo Donador
class Donador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_pat_donador = models.CharField(max_length=100)
    apellido_mat_donador = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    fecha_registro_donador = models.DateField()
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido_pat_donador}"

# Modelo Transaccion
class Transaccion(models.Model):
    monto_transaccion = models.IntegerField()
    fecha_donacion = models.DateField()
    referencia_webpay = models.CharField(max_length=100)
    estado_transaccion = models.CharField(max_length=100)

    def __str__(self):
        return self.referencia_webpay
    
from django.utils import timezone
# Modelo Donacion
class Donacion(models.Model):
    monto = models.IntegerField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Permitir valores nulos
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE)
    transaccion = models.ForeignKey(Transaccion, on_delete=models.CASCADE)
    fecha_donacion = models.DateTimeField(default=timezone.now)  # Establece una fecha predeterminada

    def __str__(self):
        return f"Donación de {self.monto} a {self.campana.nombre_campana} por {self.usuario.username}"




# Create your models here.

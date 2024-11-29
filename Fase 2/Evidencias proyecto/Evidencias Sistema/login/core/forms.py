from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
import datetime
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'required': True}),
            'first_name': forms.TextInput(attrs={'required': True}),
            'last_name': forms.TextInput(attrs={'required': True}),
            'email': forms.EmailInput(attrs={'required': True}),
            'password1': forms.PasswordInput(attrs={'required': True}),
            'password2': forms.PasswordInput(attrs={'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que todos los campos sean requeridos
        for field_name in self.fields:
            self.fields[field_name].required = True


class CampanaForm(forms.ModelForm):

    class Meta:
        model = Campana
        exclude = ['user' , 'estado','monto_donado', 'slug']
        widgets = {
            'fecha_inicio_campana': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_campana': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = datetime.date.today().isoformat()  # Convertir a formato ISO (YYYY-MM-DD)
        
        # Establecer fecha de inicio como hoy y hacer que sea solo lectura
        self.fields['fecha_inicio_campana'].initial = hoy
        self.fields['fecha_inicio_campana'].widget.attrs['readonly'] = True
        
        # Establecer la fecha mínima para fecha_fin_campana como hoy
        self.fields['fecha_fin_campana'].widget.attrs['min'] = hoy

class ModificarCampanaForm(forms.ModelForm):

    class Meta:
        model = Campana
        exclude = ['user', 'estado', 'fecha_inicio_campana', 'link_webpay', 'monto_donado']
        widgets = {
            'fecha_fin_campana': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = self.instance.fecha_inicio_campana
        fecha_fin = cleaned_data.get('fecha_fin_campana')

        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            self.add_error('fecha_fin_campana', 'La fecha de fin no puede ser anterior a la fecha de inicio de la campaña.')

        return cleaned_data
    

class CampanaFilterForm(forms.Form):
    tipo_campana = forms.ModelChoiceField(
        queryset=TipoCampana.objects.all(),
        required=False,
        empty_label="Todos los tipos de campaña",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Correo Electrónico", max_length=254)


class DonacionForm(forms.Form):
    monto_donacion = forms.DecimalField(
        min_value=1,
        decimal_places=2,
        max_digits=10,
        label="Monto a donar",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    correo_electronico = forms.EmailField(
        label="Correo electrónico (para el comprobante)",
        required=False,  # Solo requerido si el usuario no está autenticado
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        usuario_autenticado = kwargs.pop('usuario_autenticado', False)
        super().__init__(*args, **kwargs)
        if not usuario_autenticado:
            self.fields['correo_electronico'].required = True
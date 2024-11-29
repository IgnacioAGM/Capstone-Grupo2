from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from .forms import *
from django.contrib.auth import authenticate, login
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .webpay_config import webpay_transaction  # Importa la configuración de Webpay
import uuid
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


# Create your views here.

def home(request):
    return render(request, 'core/home.html')



def campanas(request):
    # Obtener los valores del formulario
    form = CampanaFilterForm(request.GET)

    # Filtrar las campañas
    campanas = Campana.objects.filter(estado='Aprobada')

    if form.is_valid() and form.cleaned_data['tipo_campana']:
        tipo_campana = form.cleaned_data['tipo_campana']
        campanas = campanas.filter(tipo_campana=tipo_campana)

    # Añadir campo de progreso calculado
    for campana in campanas:
        if campana.monto_objetivo_campana > 0:
            campana.progreso = min(100, (campana.monto_donado / campana.monto_objetivo_campana) * 100)
        else:
            campana.progreso = 0

    # Paginación
    page = request.GET.get('page', 1)
    try:
        paginator = Paginator(campanas, 9)
        campanas = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': campanas,
        'paginator': paginator,
        'form': form
    }
    return render(request, 'core/campanas.html', data)


def exit(request):
    logout(request)
    return redirect('home')


from django.contrib import messages

def register(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)

        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'], password=user_creation_form.cleaned_data['password1'])
            login(request, user)
            return redirect('home')
        else:
            # Agregar un mensaje general si el formulario no es válido
            messages.error(request, "Un campo no cumple con los requisitos. Vuelve a intentarlo.")
            data['form'] = user_creation_form  # Actualizar el formulario en el contexto con los errores

    return render(request, 'registration/register.html', data)



def agregar_campana(request):
    if request.method == 'POST':
        form = CampanaForm(request.POST, request.FILES)
        if form.is_valid():
            campana = form.save(commit=False)  # No guarda aún en la base de datos
            campana.user = request.user        # Asigna el usuario autenticado
            campana.save()                      # Guarda en la base de datos
            messages.success(request,"Campaña Creada Correctamente")                     
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


@login_required
def modificar_campana(request, uuid):
    campana = get_object_or_404(Campana, uuid=uuid)

    if request.method == 'POST':
        formulario = ModificarCampanaForm(data=request.POST, instance=campana, files=request.FILES)
        if formulario.is_valid():
            # Cambiar el estado de la campaña a "Pendiente"
            campana_modificada = formulario.save(commit=False)
            campana_modificada.estado = 'Pendiente'
            # Asegurarse de que los campos no se modifiquen
            campana_modificada.fecha_inicio_campana = campana.fecha_inicio_campana
            campana_modificada.link_webpay = campana.link_webpay
            campana_modificada.save()
            messages.success(request, "Campaña Modificada Correctamente, en estado Pendiente a Publicarse")
            return redirect(to="listar_campana")
        data = {'form': formulario}
    else:
        data = {
            'form': ModificarCampanaForm(instance=campana)
        }

    return render(request, 'core/campana/modificar.html', data)

def eliminar_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    campana.delete()
    messages.success(request, "Campaña Eliminada Correctamente")
    return redirect(to="listar_campana")



def detalle_campana(request, id):
    campana = get_object_or_404(Campana, id=id)
    data = {
        'campana': campana
    }
    return render(request, 'core/detalle_campana.html', data)


#VISTAS MODERADORES

from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_staff)
def moderar_campanas(request):
    campanas_pendientes = Campana.objects.filter(estado='Pendiente')
    return render(request, 'core/campana/moderar_campanas.html', {'campanas_pendientes': campanas_pendientes})

@user_passes_test(lambda u: u.is_staff)
def aprobar_campana(request, pk):
    campana = get_object_or_404(Campana, pk=pk)
    campana.estado = 'Aprobada'
    campana.save()
    return redirect('moderar_campanas')

@user_passes_test(lambda u: u.is_staff)
def rechazar_campana(request, pk):
    campana = get_object_or_404(Campana, pk=pk)
    campana.estado = 'Rechazada'
    campana.save()
    return redirect('moderar_campanas')


#WEBPAY

from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.webpay_plus.transaction import Transaction
@csrf_exempt
def iniciar_donacion(request, campana_id):
    campana = get_object_or_404(Campana, id=campana_id)
    if request.method == 'POST':
        monto = request.POST.get('monto_donacion')
        # Verifica si el usuario está autenticado. Si no, usa el correo proporcionado en el formulario.
        email = request.POST.get('email') if not request.user.is_authenticated else request.user.email

        if monto and int(monto) > 0 and email:
            buy_order = f"{campana_id}-{uuid.uuid4().hex[:10]}"
            session_id = str(request.user.id) if request.user.is_authenticated else str(uuid.uuid4())
            return_url = request.build_absolute_uri(reverse('confirmar_donacion'))

            response = webpay_transaction.create(buy_order, session_id, monto, return_url)

            # Guarda el correo electrónico en la sesión para usarlo más tarde
            request.session['donation_email'] = email

            return redirect(response['url'] + '?token_ws=' + response['token'])
        else:
            return HttpResponse("Debe ingresar un monto válido y un correo electrónico para donar.", status=400)

    return HttpResponse("Método no permitido", status=405)


from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from .webpay_config import webpay_transaction

@csrf_exempt
def confirmar_donacion(request):
    token_ws = request.POST.get('token_ws') or request.GET.get('token_ws')

    if token_ws:
        response = webpay_transaction.commit(token_ws)

        if response['response_code'] == 0 and response['status'] == 'AUTHORIZED':
            buy_order = response['buy_order']
            try:
                campana_id = int(buy_order.split('-')[0])
                campana = Campana.objects.get(id=campana_id)
            except (ValueError, Campana.DoesNotExist):
                return HttpResponse("Campaña no encontrada o ID inválido.", status=404)

            usuario = request.user if request.user.is_authenticated else None
            monto = response['amount']

            # Crear la transacción antes de registrar la donación
            transaccion = Transaccion.objects.create(
                monto_transaccion=monto,
                fecha_donacion=timezone.now(),
                referencia_webpay=token_ws,
                estado_transaccion='AUTHORIZED'
            )

            # Registrar la donación y asociarla con la transacción
            donacion = Donacion.objects.create(
                monto=monto,
                usuario=usuario,
                campana=campana,
                transaccion=transaccion
            )

            # Actualizar el monto total donado de la campaña
            campana.monto_donado += monto
            campana.save()

            # Obtener el correo electrónico desde la sesión
            email = request.session.get('donation_email')
            if email:
                detalles_transaccion = {
                    'fecha': transaccion.fecha_donacion,
                    'monto': transaccion.monto_transaccion,
                    'campana': campana.nombre_campana
                }
                enviar_comprobante_transaccion(email, detalles_transaccion)

            # Mensaje de éxito
            messages.success(request, "¡Donación completada exitosamente!")
            return redirect(reverse('home'))
        else:
            messages.error(request, "Hubo un error con la transacción. Por favor, inténtelo nuevamente.")
            return redirect(reverse('home'))
    return HttpResponse("No se recibió el token de transacción.", status=400)

def error(request):
    return render(request, 'core/error.html')

@login_required
def historial_donaciones(request):
    donaciones = Donacion.objects.filter(usuario=request.user).order_by('-fecha_donacion')
    return render(request, 'core/historial_donaciones.html', {'donaciones': donaciones})


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def enviar_comprobante_transaccion(email, detalles_transaccion):
    # Carga la plantilla HTML del comprobante
    html_message = render_to_string('emails/comprobante_transaccion.html', {'detalles': detalles_transaccion})
    plain_message = strip_tags(html_message)  # Versión sin formato HTML
    subject = 'Comprobante de Transacción Aprobada'

    # Envía el correo electrónico
    send_mail(
        subject,
        plain_message,
        'pruebacapstone7@gmail.com',  # Dirección de correo de origen
        [email],  # Dirección de correo del destinatario
        html_message=html_message
    )

from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "No se encontró un usuario con ese correo electrónico.")
                return redirect('password_reset_request')

            # Generar el token y el enlace de restablecimiento de contraseña
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Renderizar el contenido HTML del correo
            subject = "Solicitud de restablecimiento de contraseña"
            html_content = render_to_string('emails/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link
            })

            # Crear el correo electrónico con contenido HTML
            email_message = EmailMultiAlternatives(
                subject=subject,
                body="Has solicitado restablecer tu contraseña. Haz clic en el enlace para cambiarla.",
                from_email='pruebacapstone7@gmail.com',
                to=[user.email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, "Se ha enviado un enlace de restablecimiento de contraseña a tu correo electrónico.")
            return redirect('home')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'core/password_reset_request.html', {'form': form})



from django.contrib.auth import update_session_auth_hash
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render, redirect
from django.contrib import messages

User = get_user_model()

def custom_password_reset_confirm(request, uidb64, token):
    try:
        # Decodifica el uidb64 para obtener el id del usuario
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Verifica si el token es válido
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, user)  # Mantiene la sesión activa
                messages.success(request, "¡Tu contraseña ha sido cambiada exitosamente!")
                return redirect('home')
            else:
                messages.error(request, "Por favor, corrige los errores a continuación.")
        else:
            form = SetPasswordForm(user)
        return render(request, 'core/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "El enlace de restablecimiento de contraseña no es válido o ha expirado.")
        return redirect('password_reset_request')
from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_matricula(usuario, curso):
    asunto = f'Te has matriculado en {curso.nombre}'
    mensaje = f'Hola {usuario.get_full_name()},\n\nTe has matriculado exitosamente en el curso {curso.nombre}.'
    remitente = settings.DEFAULT_FROM_EMAIL
    destinatario = [usuario.email]
    
    send_mail(asunto, mensaje, remitente, destinatario)

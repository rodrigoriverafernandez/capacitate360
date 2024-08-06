from io import BytesIO
from tkinter import Image
from django.conf import settings
import pandas as pd
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import login
from .models import Curso, Matricula, Empleado
from django.http import JsonResponse
from .forms import RegistroForm, CursoSeleccionForm, DiplomaForm
from django.http import HttpResponse

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import enviar_correo_matricula
from django.core.mail import send_mail
from .forms import EmpleadoImportForm

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from .models import Curso

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from pdfrw import PdfReader, PdfWriter, PageMerge


def home(request):
    return render(request, 'home.html')

#def cursos(request):
#    cursos = Curso.objects.all()
#    return render(request, 'cursos/cursos.html', {'cursos': cursos})

def curso_detalle(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    matricula = None
    diploma_aprobado = False

    if request.user.is_authenticated:
        # Intentar obtener la matrícula para el usuario autenticado y el curso dado
        matricula = Matricula.objects.filter(curso=curso, usuario=request.user).first()

        if matricula:
            diploma_aprobado = matricula.aprobado_diploma

    return render(request, 'cursos/curso_detalle.html', {
        'curso': curso,
        'matricula': matricula,
        'diploma_aprobado': diploma_aprobado,
    })

def cursos(request):
    lista_cursos = Curso.objects.all()  # Asumiendo que tienes un modelo llamado Curso
    return render(request, 'cursos/cursos.html', {'cursos': lista_cursos})



@login_required
def matricularse(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    usuario = request.user

    # Verificar si el usuario ya está matriculado en el curso
    if Matricula.objects.filter(curso=curso, usuario=usuario).exists():
        messages.error(request, 'Ya estás matriculado en este curso.')
        return redirect('cursos')

    # Verificar si el curso ha alcanzado su cupo máximo
    if Matricula.objects.filter(curso=curso).count() >= curso.cupo:
        messages.error(request, 'El curso ya ha alcanzado su cupo máximo.')
        return redirect('cursos')

    if request.method == 'POST':
        Matricula.objects.create(curso=curso, usuario=usuario)
        enviar_correo_matricula(usuario, curso)  # Enviar correo electrónico
        messages.success(request, 'Te has matriculado exitosamente en el curso.')
        return redirect('mis_cursos')

    return render(request, 'cursos/matricularse.html', {'curso': curso})


@login_required
def mis_cursos(request):
    usuario = request.user
    matriculas = Matricula.objects.filter(usuario=usuario)
    cursos = [matricula.curso for matricula in matriculas]

    return render(request, 'cursos/mis_cursos.html', {'cursos': cursos})




@login_required
def listar_estudiantes(request):
    cursos = Curso.objects.all()
    cursos_con_estudiantes = []

    for curso in cursos:
        matriculas = Matricula.objects.filter(curso=curso)
        estudiantes = [matricula.usuario for matricula in matriculas]
        cursos_con_estudiantes.append({
            'curso': curso,
            'estudiantes': estudiantes,
            'total': len(estudiantes)
        })

    return render(request, 'cursos/listar_estudiantes.html', {'cursos_con_estudiantes': cursos_con_estudiantes})

@login_required
def estudiantes_por_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    matriculas = Matricula.objects.filter(curso=curso)
    estudiantes = [matricula.usuario for matricula in matriculas]
    return render(request, 'cursos/estudiantes_por_curso.html', {'curso': curso, 'estudiantes': estudiantes})


@login_required
def seleccionar_curso(request):
    if request.method == 'POST':
        form = CursoSeleccionForm(request.POST)
        if form.is_valid():
            curso_id = form.cleaned_data['curso'].id
            return redirect('estudiantes_por_curso', curso_id=curso_id)
    else:
        form = CursoSeleccionForm()
    return render(request, 'cursos/seleccionar_curso.html', {'form': form})



# Vista de registro


def registro(request):
    if request.method == 'POST':
       form = RegistroForm(request.POST, request.FILES)
       if form.is_valid():
            try:
                user = form.save(commit=False)
                user.username = user.rpe  # Usar el RPE como nombre de usuario
                user.first_name = form.cleaned_data['nombre']
                user.last_name = form.cleaned_data['apellido_paterno'] + ' ' + form.cleaned_data['apellido_materno']
                user.email = form.cleaned_data['correo']  # Asegúrate de guardar el correo
                if 'foto' in request.FILES:
                    user.foto = request.FILES['foto']
              
                user.save()
                login(request, user)  # Inicia sesión automáticamente después del registro
                messages.success(request, 'Registro exitoso. Ahora estás logueado.')
                return redirect('cursos')  # Redirige a la página de cursos disponibles
            except IntegrityError:
                form.add_error('rpe', 'Ya existe un usuario con este RPE.')
    else:
        form = RegistroForm()
    return render(request, 'cursos/registro.html', {'form': form})


def obtener_datos_empleado(request):
    rpe = request.GET.get('rpe', None)
    if rpe:
        print(f"RPE received: {rpe}")
        try:
            empleado = Empleado.objects.get(rpe=rpe)
            data = {
                'nombre': empleado.nombre,
                'apellido_paterno': empleado.apellido_paterno,
                'apellido_materno': empleado.apellido_materno,
                'correo': empleado.correo,
                'telefono': empleado.telefono,
                'area_trabajo': empleado.area_trabajo,
                'tc': empleado.tc,
                'fecha_antiguedad': empleado.fecha_antiguedad,
                'categoria_descripcion': empleado.categoria_descripcion,
                'area_adscripcion': empleado.area_adscripcion,
                'descripcion_categoria': empleado.descripcion_categoria,
            }
            print(f"Empleado data: {data}")
            return JsonResponse(data)
        except Empleado.DoesNotExist:
            print("Empleado no encontrado")
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
    else:
        print("No RPE provided")
        return JsonResponse({'error': 'No RPE provided'}, status=400)

from django.http import HttpResponse
import openpyxl
from .models import Curso, Matricula
from io import BytesIO  # Asegúrate de importar BytesIO

# **************** Exportar *************
from django.http import HttpResponse
import openpyxl
from io import BytesIO
from .models import Curso, Matricula

def exportar_estudiantes_excel(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    matriculas = Matricula.objects.filter(curso=curso)
    
    # Crear un libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Estudiantes de {curso.nombre}"
    
    # Escribir el encabezado
    ws.append([
        "RPE", "Nombre", "Apellido Paterno", "Apellido Materno", "Correo",
        "Teléfono", "Área de Trabajo", "Tipo de Empleado", "Fecha de Antigüedad",
        "Descripción de Categoría", "Área de Adscripción", "Descripción Categoría"
    ])
    
    # Escribir los datos de los estudiantes
    def sanitizar_valor(valor):
        return valor if valor is not None else ''

    for matricula in matriculas:
        usuario = matricula.usuario
        ws.append([
            sanitizar_valor(usuario.rpe),
            sanitizar_valor(usuario.nombre),
            sanitizar_valor(usuario.apellido_paterno),
            sanitizar_valor(usuario.apellido_materno),
            sanitizar_valor(usuario.correo),
            sanitizar_valor(usuario.telefono),
            sanitizar_valor(usuario.area_trabajo),
            sanitizar_valor(usuario.tc),
            sanitizar_valor(usuario.fecha_antiguedad),
            sanitizar_valor(usuario.categoria_descripcion),
            sanitizar_valor(usuario.area_adscripcion.nombre if usuario.area_adscripcion else ''),
            sanitizar_valor(usuario.descripcion_categoria)
        ])
    
    # Guardar el libro de Excel en memoria
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Crear una respuesta HTTP
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=estudiantes_{curso.nombre}.xlsx'
    return response

# Vista de Contacto 

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        # Aquí puedes manejar el envío del correo
        send_mail(
            f'Mensaje de {name}',
            message,
            email,
            ['info@capacitate360.com'],
            fail_silently=False,
        )
        messages.success(request, 'Tu mensaje ha sido enviado con éxito.')
        return redirect('contact')
    return render(request, 'cursos/contact.html')



from django.http import HttpResponse
from .models import Empleado



def importar_empleados(request):
    if request.method == 'POST':
        form = EmpleadoImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)

            # Imprimir nombres de las columnas para verificar
            print("Columnas en el archivo Excel:", df.columns)

            required_columns = [
                'rpe', 'nombre', 'apellido_paterno', 'apellido_materno', 'fecha_antiguedad', 
                'categoria_descripcion', 'area_adscripcion', 'area_trabajo', 'descripcion_categoria', 
                'correo', 'telefono', 'tc'
            ]

            # Verificar si todas las columnas requeridas están presentes
            if not all(column in df.columns for column in required_columns):
                return HttpResponse("Error: El archivo Excel no contiene todas las columnas requeridas. Columnas presentes: " + ", ".join(df.columns))

            for index, row in df.iterrows():
                Empleado.objects.update_or_create(
                    rpe=row['rpe'],
                    defaults={
                        'nombre': row['nombre'],
                        'apellido_paterno': row['apellido_paterno'],
                        'apellido_materno': row['apellido_materno'],
                        'fecha_antiguedad': row['fecha_antiguedad'],
                        'categoria_descripcion': row['categoria_descripcion'],
                        'area_adscripcion': row['area_adscripcion'],
                        'area_trabajo': row['area_trabajo'],
                        'descripcion_categoria': row['descripcion_categoria'],
                        'correo': row['correo'],
                        'telefono': row['telefono'],
                        'tc': row['tc'],
                    }
                )
            return HttpResponse("Empleados importados exitosamente.")
    else:
        form = EmpleadoImportForm()
    
    return render(request, 'cursos/importar_empleados.html', {'form': form})


from xhtml2pdf import pisa

def generar_pdf_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    html_string = render_to_string('cursos/curso_pdf.html', {'curso': curso})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{curso.nombre}.pdf"'
    
    # Crear el PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    # Verificar errores
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    
    return response

from django.http import HttpResponse, Http404
from .models import Matricula
from django.conf import settings
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

def generar_diploma(request, matricula_id):
    matricula = Matricula.objects.get(id=matricula_id)

    # Primero, verificar si existe un archivo de diploma subido
    if matricula.diploma_archivo and matricula.diploma_archivo.path and os.path.exists(matricula.diploma_archivo.path):
        with open(matricula.diploma_archivo.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{matricula.diploma_archivo.name}"'
            return response

    # Si no hay un archivo subido, se procede a generar el diploma dinámicamente
    usuario = matricula.usuario
    curso = matricula.curso

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="diploma_{usuario.rpe}_{curso.nombre}.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Verificar si STATIC_ROOT está configurado, de lo contrario, usar STATICFILES_DIRS
    if settings.STATIC_ROOT:
        watermark_path = os.path.join(settings.STATIC_ROOT, 'img', 'watermark.png')
    else:
        watermark_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'watermark.png')
    
    # Marca de agua de imagen con transparencia
    if os.path.exists(watermark_path):
        watermark = Image.open(watermark_path)
        watermark = watermark.convert("RGBA")
        
        # Ajustar la opacidad de la marca de agua
        alpha = watermark.split()[3]
        alpha = alpha.point(lambda p: p * 0.2)  # Cambia 0.2 por el nivel de transparencia deseado
        watermark.putalpha(alpha)

        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_watermark.png')
        watermark.save(temp_path)
        
        watermark_img = ImageReader(temp_path)
        c.drawImage(watermark_img, 0, 0, width=width, height=height, mask='auto')
        os.remove(temp_path)  # Eliminar la marca de agua temporal después de usarla

    # Títulos y cabecera
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 40, "Comisión Federal de Electricidad")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 70, "Gerencia de Abastecimiento")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 90, "Subgerencia de Regulación de Contrataciones")

    # Título del diploma
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 170, "Diploma de Finalización de Curso")

    # Agregar nombre del estudiante
    c.setFont("Helvetica-Bold", 18)
    nombre_completo = f"{usuario.first_name} {usuario.last_name}"
    c.drawCentredString(width / 2, height - 240, nombre_completo)

    # Nombre del curso
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 270, f"Por completar el curso '{curso.nombre}'")

    # Nombre del profesor
    profesor_nombre = curso.profesor.get_full_name()
    c.drawCentredString(width / 2, height - 310, f"Impartido por: {profesor_nombre}")

    # Foto del estudiante (arriba a la izquierda)
    if usuario.foto and usuario.foto.path:
        foto_path = usuario.foto.path
        if os.path.exists(foto_path):
            img = ImageReader(foto_path)
            img_width = 100  # Ancho de la imagen
            img_height = 90 # Alto de la imagen
            c.drawImage(img, 30, height - 100, width=img_width, height=img_height)  # Ajusta la posición y el tamaño
        else:
            print("Foto does not exist at", foto_path)
    else:
        print("Foto path is None")

    # Fecha de finalización
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 530, "Fecha de finalización: " + curso.fecha_fin.strftime("%d/%m/%Y"))

    # Sección de firmas
    firma_y = height - 700  # Ajusta esta posición según se necesite
    espacio_entre_firmas = 40  # Espacio vertical entre firmas

    # Firma del instructor
    c.line(width / 6, firma_y, width / 2.2, firma_y)  # Línea de firma
    c.drawString(width / 6, firma_y - 10, "Instructor")

    # Firma del gerente
    c.line(width / 2, firma_y, 5 * width / 6, firma_y)  # Línea de firma
    c.drawString(width / 2, firma_y - 10, "Gerente")

    # Firma del subgerente
    c.line(width / 6, firma_y - espacio_entre_firmas, width / 2.2, firma_y - espacio_entre_firmas)
    c.drawString(width / 6, firma_y - espacio_entre_firmas - 10, "Subgerente")

    # Cerrar el PDF
    c.showPage()
    c.save()

    return response
    

import os


def descargar_diploma_firmado(request, matricula_id):
    matricula = get_object_or_404(Matricula, id=matricula_id, usuario=request.user)

# Asumiendo que el archivo PDF está almacenado como "diplomas/firmados/usuario_curso.pdf"
    nombre_archivo = f"{matricula.usuario.username}_{matricula.curso.nombre}.pdf"
    path_archivo = os.path.join('/path/to/diplomas/firmados/', nombre_archivo)

    if os.path.exists(path_archivo):
        with open(path_archivo, 'rb') as archivo:
            response = HttpResponse(archivo.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response
    else:
        return HttpResponse('Diploma no disponible.', status=404)
    
def subir_diploma(request, matricula_id):
    matricula = get_object_or_404(Matricula, id=matricula_id)

    if request.method == 'POST':
        form = DiplomaForm(request.POST, request.FILES, instance=matricula)
        if form.is_valid():
            form.save()
            matricula.aprobado_diploma = True  # Marca el diploma como aprobado
            matricula.save()
            return redirect('curso_detalle', curso_id=matricula.curso.id)
    else:
        form = DiplomaForm(instance=matricula)

    return render(request, 'cursos/subir_diploma.html', {'form': form, 'matricula': matricula})    
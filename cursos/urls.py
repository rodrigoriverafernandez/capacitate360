from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from cursos import views  # Asegúrate de importar el módulo de vistas correctamente

urlpatterns = [
    path('', views.home, name='home'),  # Página principal
   
    path('registro/', views.registro, name='registro'),
    path('matricularse/<int:curso_id>/', views.matricularse, name='matricularse'),
    path('mis-cursos/', views.mis_cursos, name='mis_cursos'),
    path('cursos/', views.cursos, name='cursos'),  # Ruta para la lista de cursos
    path('curso/<int:curso_id>/', views.curso_detalle, name='curso_detalle'),  # Ruta para el detalle del curso
    path('login/', auth_views.LoginView.as_view(template_name='cursos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('listar-estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),
    path('estudiantes-por-curso/<int:curso_id>/', views.estudiantes_por_curso, name='estudiantes_por_curso'),
    path('seleccionar-curso/', views.seleccionar_curso, name='seleccionar_curso'),
    path('obtener-datos-empleado/', views.obtener_datos_empleado, name='obtener_datos_empleado'),
    path('exportar-estudiantes-excel/<int:curso_id>/', views.exportar_estudiantes_excel, name='exportar_estudiantes_excel'),
     path('contact/', views.contact, name='contact'),
    path('curso/<int:curso_id>/pdf/', views.generar_pdf_curso, name='curso_pdf'),
    path('diploma/<int:matricula_id>/', views.generar_diploma, name='generar_diploma'),
    path('subir-diploma/<int:matricula_id>/', views.subir_diploma, name='subir_diploma'),
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

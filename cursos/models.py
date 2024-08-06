from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser

class Empleado(models.Model):
    rpe = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    fecha_antiguedad = models.DateField(null=True, blank=True)
    categoria_descripcion = models.CharField(max_length=200, null=True, blank=True)
    area_adscripcion = models.CharField(max_length=100, null=True, blank=True)
    area_trabajo = models.CharField(max_length=100, null=True, blank=True)
    descripcion_categoria = models.TextField(null=True, blank=True)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    tc = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
    

class AreaAdscripcion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, rpe, password=None, **extra_fields):
        if not rpe:
            raise ValueError('El campo RPE debe ser establecido')
        user = self.model(rpe=rpe, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rpe, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(rpe, password, **extra_fields)

class Usuario(AbstractUser):
    rpe = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    area_trabajo = models.CharField(max_length=100)
    tc = models.CharField(max_length=2)
    fecha_antiguedad = models.DateField(null=True, blank=True)
    categoria_descripcion = models.CharField(max_length=200, null=True, blank=True)
    area_adscripcion = models.ForeignKey(AreaAdscripcion, null=True, blank=True, on_delete=models.SET_NULL)
    descripcion_categoria = models.TextField(null=True, blank=True)
    foto = models.ImageField(upload_to='fotos_estudiantes/', null=True, blank=True)

    USERNAME_FIELD = 'rpe'
    REQUIRED_FIELDS = ['correo', 'nombre', 'apellido_paterno', 'apellido_materno']

    objects = UsuarioManager()

    def __str__(self):
        return self.rpe


class Curso(models.Model):
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField()
    publico = models.BooleanField(default=True)
    profesor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cursos_dictados')
    cupo = models.IntegerField()
    valor_en_puntos = models.IntegerField()
    icon = models.CharField(max_length=50, default='fas fa-book-open')
    imagen = models.ImageField(upload_to='cursos/', null=True, blank=True)
    contenido = models.TextField(blank=True, null=True)
    documento_pdf = models.FileField(upload_to='documentos/', null=True, blank=True)
    plantilla_diploma = models.FileField(upload_to='plantillas_diplomas/', null=True, blank=True)

    def __str__(self):
        return self.nombre


    
class Matricula(models.Model):
    # Campos existentes...
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    aprobado_diploma = models.BooleanField(default=False)
    diploma_archivo = models.FileField(upload_to='diplomas/', null=True, blank=True)

    def __str__(self):
        return f"{self.usuario} - {self.curso}"
    

class DiplomaFirmado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    archivo_pdf = models.FileField(upload_to='diplomas/firmados/')
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Diploma de {self.usuario} para {self.curso}"  
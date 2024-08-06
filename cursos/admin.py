from django import forms
from django.contrib import admin
from .models import Usuario, Curso, Matricula, Empleado
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Empleado, AreaAdscripcion

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        # Comprobar si el correo ya existe para otro usuario
        if Usuario.objects.exclude(pk=self.instance.pk).filter(correo=correo).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return correo

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'rpe', 'first_name', 'last_name', 'email', 'area_adscripcion', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('rpe', 'first_name', 'last_name', 'email', 'area_adscripcion', 'foto')}),
        ('Permisos', {'fields': ('is_staff', 'is_active')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'rpe', 'first_name', 'last_name', 'email', 'password1', 'password2', 'area_adscripcion', 'foto'),
        }),
    )


class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'profesor', 'cupo', 'valor_en_puntos')
    search_fields = ('nombre', 'profesor__username')

admin.site.register(Curso, CursoAdmin)





class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('rpe', 'nombre', 'apellido_paterno', 'apellido_materno', 'fecha_antiguedad', 'categoria_descripcion', 'area_adscripcion', 'area_trabajo', 'descripcion_categoria', 'correo', 'telefono', 'tc')
    search_fields = ('rpe', 'nombre', 'apellido_paterno', 'apellido_materno', 'correo')
    ordering = ('rpe',)

admin.site.register(Empleado, EmpleadoAdmin)

# Opcional: Puedes definir una clase personalizada de administrador
class AreaAdscripcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')

# Registrar el modelo y la clase de administrador
admin.site.register(AreaAdscripcion, AreaAdscripcionAdmin)


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'curso', 'aprobado_diploma', 'diploma_archivo')
    list_filter = ('aprobado_diploma',)
    actions = ['aprobar_diploma']

    def aprobar_diploma(self, request, queryset):
        queryset.update(aprobado_diploma=True)
        self.message_user(request, "Diplomas aprobados correctamente.")
    aprobar_diploma.short_description = "Aprobar diplomas seleccionados"

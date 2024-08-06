# cursos/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Curso,Matricula
from .models import Usuario, AreaAdscripcion

class RegistroForm(UserCreationForm):
    foto = forms.ImageField(required=False)  # Añadir campo de foto

    class Meta:
        model = Usuario
        fields = [
            'rpe', 'nombre', 'apellido_paterno', 'apellido_materno',
            'correo', 'telefono', 'area_adscripcion', 'password1', 'password2', 'foto'
        ]
        labels = {
            'rpe': 'RPE (será tu nombre de usuario)',
        }

    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        self.fields['rpe'].widget.attrs.update({'class': 'form-control', 'id': 'id_rpe'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'id': 'id_nombre'})
        self.fields['apellido_paterno'].widget.attrs.update({'class': 'form-control', 'id': 'id_apellido_paterno'})
        self.fields['apellido_materno'].widget.attrs.update({'class': 'form-control', 'id': 'id_apellido_materno'})
        self.fields['correo'].widget.attrs.update({'class': 'form-control', 'id': 'id_correo'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control', 'id': 'id_telefono'})
        self.fields['area_adscripcion'].queryset = AreaAdscripcion.objects.all()
        self.fields['area_adscripcion'].widget.attrs.update({'class': 'form-control', 'id': 'id_area_adscripcion'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'id': 'id_password1'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'id': 'id_password2'})
        self.fields['foto'].widget.attrs.update({'class': 'form-control', 'id': 'id_foto'})

    def clean_rpe(self):
        rpe = self.cleaned_data.get('rpe')
        if Usuario.objects.filter(rpe=rpe).exists():
            raise forms.ValidationError('Ya existe un usuario con este RPE.')
        return rpe

    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)
        user.username = self.cleaned_data['rpe']
        user.foto = self.cleaned_data.get('foto', None)  # Guardar foto

        if commit:
            user.save()
        return user




    
class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['id']  # Este campo es de tipo ForeignKey


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'fecha_inicio', 'fecha_fin', 'descripcion', 'publico', 'profesor', 'cupo', 'valor_en_puntos']



class CursoSeleccionForm(forms.Form):
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label="Seleccione un curso", widget=forms.Select(attrs={'class': 'form-control'}))




class EmpleadoImportForm(forms.Form):
    file = forms.FileField(label='Selecciona un archivo Excel')


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        # Ignorar la validación si estamos editando el mismo usuario
        if self.instance.pk is not None:
            if Usuario.objects.exclude(pk=self.instance.pk).filter(correo=correo).exists():
                raise forms.ValidationError('Ya existe un usuario con este correo.')
        else:
            if Usuario.objects.filter(correo=correo).exists():
                raise forms.ValidationError('Ya existe un usuario con este correo.')
        return correo
    
class DiplomaForm(forms.ModelForm):
    class Meta:
      model = Matricula
      fields = ['diploma_archivo']
# Generated by Django 3.2.7 on 2024-07-24 19:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0003_auto_20240722_1130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empleado',
            name='area',
        ),
        migrations.RemoveField(
            model_name='empleado',
            name='tipo_empleado',
        ),
        migrations.AddField(
            model_name='empleado',
            name='area_adscripcion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='empleado',
            name='area_trabajo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='empleado',
            name='categoria_descripcion',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='empleado',
            name='descripcion_categoria',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='empleado',
            name='fecha_antiguedad',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='empleado',
            name='tc',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='curso',
            name='profesor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cursos_dictados', to=settings.AUTH_USER_MODEL),
        ),
    ]

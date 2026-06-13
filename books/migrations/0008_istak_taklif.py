import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0007_sharh'),
    ]

    operations = [
        migrations.AddField(
            model_name='almashitirish',
            name='taklif_kitob',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='taklif_qilingan', to='books.kitob',
                help_text='Almashtirishga taklif qilingan kitob (ixtiyoriy)',
            ),
        ),
        migrations.CreateModel(
            name='Istak',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomi', models.CharField(max_length=200)),
                ('muallif', models.CharField(blank=True, max_length=100)),
                ('izoh', models.TextField(blank=True)),
                ('topildi', models.BooleanField(default=False)),
                ('yaratildi', models.DateTimeField(auto_now_add=True)),
                ('foydalanuvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='istaklar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-yaratildi'],
            },
        ),
    ]

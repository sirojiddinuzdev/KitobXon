import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0004_profil_avatar_bio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bildirishnoma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matn', models.CharField(max_length=255)),
                ('havola', models.CharField(blank=True, max_length=200)),
                ('turi', models.CharField(choices=[('info', 'Info'), ('success', 'Muvaffaqiyat'), ('warning', 'Ogohlantirish')], default='info', max_length=20)),
                ('oqilgan', models.BooleanField(default=False)),
                ('yaratildi', models.DateTimeField(auto_now_add=True)),
                ('foydalanuvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bildirishnomalar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-yaratildi'],
            },
        ),
    ]

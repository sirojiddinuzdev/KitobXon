import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0005_alter_kitob_hudud'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kitob',
            options={'ordering': ['-yaratildi']},
        ),
        migrations.AlterModelOptions(
            name='almashitirish',
            options={'ordering': ['-yaratildi']},
        ),
        migrations.AlterField(
            model_name='kitob',
            name='janr',
            field=models.CharField(
                choices=[
                    ('badiiy', 'Badiiy'),
                    ('Selfhelp', 'Self Help'),
                    ('it', 'IT'),
                    ('romantik', 'Romantik'),
                    ('ilmiy_ommabop', 'Ilmiy-Ommabop'),
                    ('biznes_iqtisod', 'Biznes-Iqtisod'),
                    ('psixologiya', 'Psixologiya'),
                ],
                default='badiiy',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='Sevimli',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yaratildi', models.DateTimeField(auto_now_add=True)),
                ('kitob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sevib_qolinganlar', to='books.kitob')),
                ('foydalanuvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sevimlilar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-yaratildi'],
                'unique_together': {('foydalanuvchi', 'kitob')},
            },
        ),
    ]

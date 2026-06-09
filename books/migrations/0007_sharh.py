import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0006_sevimli_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sharh',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baho', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('matn', models.TextField(blank=True)),
                ('yaratildi', models.DateTimeField(auto_now_add=True)),
                ('kitob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharhlar', to='books.kitob')),
                ('muallif', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharhlar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-yaratildi'],
                'unique_together': {('kitob', 'muallif')},
            },
        ),
    ]

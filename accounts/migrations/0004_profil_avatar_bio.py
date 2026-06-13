from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_delete_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
        migrations.AddField(
            model_name='profil',
            name='bio',
            field=models.TextField(blank=True, max_length=300),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='welcome_email_sent',
            field=models.BooleanField(default=False, verbose_name='تم إرسال رسالة الترحيب'),
        ),
    ]

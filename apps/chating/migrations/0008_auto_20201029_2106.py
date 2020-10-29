# Generated by Django 3.1.2 on 2020-10-29 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users_profile', '0002_profile_status'),
        ('chating', '0007_auto_20200827_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chating.commonchat'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users_profile.profile'),
        ),
        migrations.AlterField(
            model_name='privatechat',
            name='common_chat',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='chating.commonchat'),
        ),
        migrations.AlterField(
            model_name='privatechat',
            name='profile_1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_1', to='users_profile.profile'),
        ),
        migrations.AlterField(
            model_name='privatechat',
            name='profile_2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_2', to='users_profile.profile'),
        ),
        migrations.AlterField(
            model_name='savedmessageschat',
            name='common_chat',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='chating.commonchat'),
        ),
        migrations.AlterField(
            model_name='savedmessageschat',
            name='profile',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='users_profile.profile'),
        ),
        migrations.DeleteModel(
            name='GroupChat',
        ),
    ]

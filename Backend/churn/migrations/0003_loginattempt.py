# Generated migration file for LoginAttempt model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('churn', '0002_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('success', models.BooleanField(null=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('error_message', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Login Attempt',
                'verbose_name_plural': 'Login Attempts',
                'db_table': 'audit_login_attempts',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='loginattempt',
            index=models.Index(fields=['email', '-timestamp'], name='audit_logi_email_idx'),
        ),
        migrations.AddIndex(
            model_name='loginattempt',
            index=models.Index(fields=['ip_address', '-timestamp'], name='audit_logi_ip_idx'),
        ),
        migrations.AddIndex(
            model_name='loginattempt',
            index=models.Index(fields=['success', '-timestamp'], name='audit_logi_success_idx'),
        ),
        migrations.AddIndex(
            model_name='loginattempt',
            index=models.Index(fields=['-timestamp'], name='audit_logi_timestamp_idx'),
        ),
    ]

# Generated by Django 5.2.2 on 2025-06-07 12:14

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=100)),
                ('business_name', models.CharField(max_length=100)),
                ('business_address', models.TextField()),
                ('primary_phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$')])),
                ('secondary_phone', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$')])),
                ('business_email', models.EmailField(max_length=254)),
                ('gst_number', models.CharField(blank=True, max_length=20)),
                ('industry_type', models.CharField(choices=[('web_design', 'Web Design & Development'), ('real_estate', 'Real Estate'), ('home_decor', 'Home Decor'), ('studio_accessories', 'Studio Accessories'), ('handloom', 'Handloom'), ('other', 'Other')], max_length=50)),
                ('work_required', models.CharField(max_length=100)),
                ('project_handover_date', models.DateField()),
                ('remarks', models.TextField(blank=True)),
                ('project_status', models.CharField(choices=[('metalized', 'Metalized'), ('call_back', 'Call Back'), ('not_interested', 'Not Interested'), ('already_paid', 'Already Paid'), ('transferred', 'Transferred')], default='call_back', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('advance_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='added_clients', to=settings.AUTH_USER_MODEL)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_clients', to=settings.AUTH_USER_MODEL)),
                ('transferred_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transferred_clients', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_added'],
            },
        ),
    ]

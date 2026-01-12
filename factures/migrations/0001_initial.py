import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('commandes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_facture', models.CharField(max_length=50, unique=True)),
                ('date_emission', models.DateField(auto_now_add=True)),
                ('date_echeance', models.DateField(blank=True, null=True)),
                ('pdf', models.FileField(blank=True, null=True, upload_to='factures/')),
                ('commande', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='facture', to='commandes.commande')),
            ],
        ),
    ]

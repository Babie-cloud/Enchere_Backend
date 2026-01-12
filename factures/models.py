# factures/models.py
from django.db import models
from commandes.models import Commande

class Facture(models.Model):
    commande = models.OneToOneField(
        Commande,
        on_delete=models.PROTECT,
        related_name='facture'
    )
    numero_facture = models.CharField(max_length=50, unique=True)
    date_emission = models.DateField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)
    pdf = models.FileField(upload_to='factures/', null=True, blank=True)

    def __str__(self):
        return f"Facture {self.numero_facture} - {self.commande}"

    def save(self, *args, **kwargs):
        if not self.numero_facture:
            # Génère un numéro auto : F-2025-0001
            last = Facture.objects.all().order_by('id').last()
            if not last:
                self.numero_facture = "F-2025-0001"
            else:
                num = int(last.numero_facture.split('-')[-1]) + 1
                self.numero_facture = f"F-2025-{num:04d}"
        super().save(*args, **kwargs)
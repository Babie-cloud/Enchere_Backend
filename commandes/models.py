# commandes/models.py
from django.db import models
from users.models import Utilisateur
from produits.models import Produit


# ===================== PANIER =====================
class Panier(models.Model):
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    utilisateur = models.OneToOneField(
        Utilisateur,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='panier'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.utilisateur or self.session_key}"


class PanierItem(models.Model):
    panier = models.ForeignKey(Panier, related_name='items', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('panier', 'produit')

    def subtotal(self):
        return self.produit.prix * self.quantite

    def __str__(self):
        titre = self.produit.safe_translation_getter("titre", f"Produit #{self.produit.pk}")
        return f"{self.quantite} × {titre}"


# ===================== COMMANDE =====================
class Commande(models.Model):
    client = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='commandes_passees',
        # limit_choices_to={'role': Role.CLIENT}
    )
    date_commande = models.DateTimeField(auto_now_add=True)
    payee = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Commande #{self.id} – {self.client}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, related_name='lignes', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.prix_unitaire * self.quantite

    def __str__(self):
        titre = self.produit.safe_translation_getter("titre", f"Produit #{self.produit.pk}")
        return f"{self.quantite} × {titre}"
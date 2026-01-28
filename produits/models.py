from django.db import models
from users.models import Utilisateur

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Produit(models.Model):
    vendeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='produits_vendu', limit_choices_to={'role': 'VENDEUR'})
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    titre = models.CharField(max_length=255, verbose_name="Titre / Nom")
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0, help_text="Stock de base hors variantes")
    poids = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    volume = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    approuve = models.BooleanField(default=True) # Corrigé : True par défaut
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

class ProductImage(models.Model):
    produit = models.ForeignKey(Produit, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='produits/images/')
    alt_text = models.CharField(max_length=255, blank=True)
    ordre = models.PositiveIntegerField(default=0)

class ProductVariant(models.Model):
    produit = models.ForeignKey(Produit, related_name='variantes', on_delete=models.CASCADE) #
    longueur = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    couleur = models.CharField(max_length=50, blank=True)
    epaisseur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    reference_sku = models.CharField(max_length=100, blank=True)
    prix_supplement = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)
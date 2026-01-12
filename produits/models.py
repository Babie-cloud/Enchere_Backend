from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from users.models import Utilisateur


class Categorie(TranslatableModel):
    """
    Catégorie de produits – nom traduit dans plusieurs langues
    """
    translations = TranslatedFields(
        nom=models.CharField(
            max_length=100,
            verbose_name="Nom de la catégorie"
            # unique=True enlevé → évite les erreurs d'unicité par langue avec parler
        )
    )

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['translations__nom']

    def __str__(self):
        return self.safe_translation_getter("nom", "Catégorie sans nom")


class Produit(TranslatableModel):
    """
    Modèle Produit avec support multilingue complet via django-parler
    """
    # Champs non traduits
    vendeur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='produits_vendu',
        limit_choices_to={'role': 'VENDEUR'},
        verbose_name="Vendeur"
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produits',
        verbose_name="Catégorie"
    )
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de base")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock global")
    poids = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True,
        help_text="Poids en kg", verbose_name="Poids"
    )
    volume = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        help_text="Volume en m³", verbose_name="Volume"
    )
    approuve = models.BooleanField(default=False, verbose_name="Approuvé")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    # Champs traduits
    translations = TranslatedFields(
        titre=models.CharField(max_length=255, verbose_name="Titre/Nom du produit"),
        description=models.TextField(blank=True, verbose_name="Description"),
    )

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-date_creation']

    def __str__(self):
        return self.safe_translation_getter("titre", f"Produit #{self.pk}")


class ProductImage(models.Model):
    produit = models.ForeignKey(Produit, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='produits/images/', verbose_name="Image")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Texte alternatif")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ['ordre']
        verbose_name = "Image produit"
        verbose_name_plural = "Images produit"


class ProductVariant(models.Model):
    produit = models.ForeignKey(Produit, related_name='variantes', on_delete=models.CASCADE)
    longueur = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Longueur (mm)")
    couleur = models.CharField(max_length=50, blank=True, verbose_name="Couleur")
    epaisseur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Épaisseur (mm)")
    reference_sku = models.CharField(max_length=100, blank=True, verbose_name="Référence SKU")
    prix_supplement = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Supplément prix")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock de la variante")

    class Meta:
        verbose_name = "Variante produit"
        verbose_name_plural = "Variantes produit"

    def __str__(self):
        details = []
        if self.longueur: details.append(f"{self.longueur}mm")
        if self.couleur: details.append(self.couleur)
        if self.epaisseur: details.append(f"{self.epaisseur}mm")
        variant_name = " ".join(details) or "Variante base"
        return f"{self.produit} - {variant_name}"
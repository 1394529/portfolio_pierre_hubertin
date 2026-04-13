"""
Core models for Pierre Hubertin's portfolio.
All content is managed through Django Admin.
"""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Project(models.Model):
    """Data / BI project showcase entry."""

    CATEGORY_CHOICES = [
        ('powerbi', 'Power BI'),
        ('sql', 'SQL / Data Modeling'),
        ('python', 'Python / ETL'),
        ('ml', 'Machine Learning'),
        ('dashboard', 'Dashboard'),
        ('other', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('published', 'Publié'),
        ('draft', 'Brouillon'),
        ('archived', 'Archivé'),
    ]

    title = models.CharField('Titre', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField('Catégorie', max_length=30, choices=CATEGORY_CHOICES, default='powerbi')
    short_description = models.CharField('Description courte', max_length=300)
    long_description = models.TextField('Description détaillée', blank=True)
    technologies = models.CharField('Technologies (virgule-séparées)', max_length=500,
                                    help_text='Ex: Power BI, DAX, SQL Server, Python')
    thumbnail = models.ImageField('Miniature', upload_to='projects/thumbnails/', blank=True, null=True)
    live_url = models.URLField('URL Démonstration', blank=True)
    github_url = models.URLField('URL GitHub', blank=True)
    featured = models.BooleanField('Projet vedette', default=False)
    order = models.PositiveIntegerField('Ordre d\'affichage', default=0)
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='published')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_technologies_list(self):
        """Returns technologies as a cleaned list."""
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    @property
    def is_published(self):
        return self.status == 'published'


class SkillCategory(models.Model):
    """Groups skills (e.g., BI Tools, Databases, Languages)."""
    name = models.CharField('Nom', max_length=100)
    icon = models.CharField('Icône CSS/SVG class', max_length=100, blank=True,
                            help_text='Classe CSS ou identifiant SVG icon')
    order = models.PositiveIntegerField('Ordre', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Catégorie de compétence'
        verbose_name_plural = 'Catégories de compétences'

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Individual technical skill with proficiency level."""

    LEVEL_CHOICES = [
        (1, 'Débutant'),
        (2, 'Intermédiaire'),
        (3, 'Avancé'),
        (4, 'Expert'),
        (5, 'Maître'),
    ]

    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE,
                                  related_name='skills', verbose_name='Catégorie')
    name = models.CharField('Nom', max_length=100)
    level = models.PositiveSmallIntegerField('Niveau (1-5)', choices=LEVEL_CHOICES, default=3)
    percentage = models.PositiveSmallIntegerField('Pourcentage (0-100)', default=80)
    icon_class = models.CharField('Icône', max_length=100, blank=True)
    order = models.PositiveIntegerField('Ordre', default=0)

    class Meta:
        ordering = ['category__order', 'order']
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    def get_stars(self):
        """Returns list of booleans for star display."""
        return [i < self.level for i in range(5)]


class BlogPost(models.Model):
    """Technical article / insight entry."""

    STATUS_CHOICES = [
        ('published', 'Publié'),
        ('draft', 'Brouillon'),
    ]

    title = models.CharField('Titre', max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.CharField('Extrait', max_length=500)
    content = models.TextField('Contenu (HTML ou Markdown)')
    tags = models.CharField('Tags (virgule-séparés)', max_length=300, blank=True)
    cover_image = models.ImageField('Image de couverture', upload_to='blog/covers/', blank=True, null=True)
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField('Date de publication', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Article de blog'
        verbose_name_plural = 'Articles de blog'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def is_published(self):
        return self.status == 'published'


class ContactMessage(models.Model):
    """Messages received via contact form."""

    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('archived', 'Archivé'),
    ]

    name = models.CharField('Nom', max_length=200)
    email = models.EmailField('Courriel')
    subject = models.CharField('Sujet', max_length=300)
    message = models.TextField('Message')
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField('Adresse IP', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'

    def __str__(self):
        return f"{self.name} — {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

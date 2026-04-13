from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Skill, SkillCategory, BlogPost, ContactMessage


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'featured', 'status', 'order', 'updated_at']
    list_filter = ['category', 'status', 'featured']
    list_editable = ['featured', 'status', 'order']
    search_fields = ['title', 'short_description', 'technologies']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Identification', {'fields': ('title', 'slug', 'category', 'status', 'featured', 'order')}),
        ('Contenu', {'fields': ('short_description', 'long_description', 'technologies', 'thumbnail')}),
        ('Liens', {'fields': ('live_url', 'github_url')}),
    )


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 3
    fields = ['name', 'level', 'percentage', 'icon_class', 'order']


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    inlines = [SkillInline]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at', 'updated_at']
    list_filter = ['status']
    search_fields = ['title', 'excerpt', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Identification', {'fields': ('title', 'slug', 'status', 'tags')}),
        ('Contenu', {'fields': ('excerpt', 'content', 'cover_image')}),
        ('Publication', {'fields': ('published_at',)}),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['name', 'email', 'subject', 'message', 'ip_address', 'created_at']

    def has_add_permission(self, request):
        return False

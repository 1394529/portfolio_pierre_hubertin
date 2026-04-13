"""
Views for the Pierre Hubertin portfolio.
"""

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page

from .models import Project, Skill, SkillCategory, BlogPost, ContactMessage
from .forms import ContactForm

from django.http import HttpResponse
from .models import Project

def test(request):
    return HttpResponse(Project.objects.count())

logger = logging.getLogger('core')


def index(request):
    """Main portfolio page — all sections loaded together."""
    projects = Project.objects.filter(status='published').order_by('order', '-created_at')
    featured_projects = projects.filter(featured=True)
    skill_categories = SkillCategory.objects.prefetch_related('skills').all()
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:3]

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            return _handle_contact_form(request, form)
    else:
        form = ContactForm()

    context = {
        'projects': projects,
        'featured_projects': featured_projects,
        'skill_categories': skill_categories,
        'recent_posts': recent_posts,
        'contact_form': form,
        'page_title': 'Pierre Hubertin — Data Analyst Power BI | SQL | BI Reporting',
        'meta_description': (
            'Analyste de données spécialisé Power BI, SQL et optimisation '
            'du reporting financier. Découvrez mes projets BI/IA et mon expertise.'
        ),
    }
    return render(request, 'index.html', context)


def project_detail(request, slug):
    """Detail page for a single project."""
    project = get_object_or_404(Project, slug=slug, status='published')
    related = (Project.objects
               .filter(status='published', category=project.category)
               .exclude(pk=project.pk)[:3])
    return render(request, 'core/project_detail.html', {
        'project': project,
        'related_projects': related,
        'page_title': f'{project.title} — Pierre Hubertin',
    })


def blog_list(request):
    """All published blog posts."""
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')
    return render(request, 'core/blog_list.html', {
        'posts': posts,
        'page_title': 'Articles — Pierre Hubertin',
    })


def blog_detail(request, slug):
    """Single blog post."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    return render(request, 'core/blog_detail.html', {
        'post': post,
        'page_title': f'{post.title} — Pierre Hubertin',
    })


@require_POST
def contact_ajax(request):
    """AJAX endpoint for contact form submission."""
    form = ContactForm(request.POST)
    if form.is_valid():
        response = _handle_contact_form(request, form, ajax=True)
        return response
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


def _handle_contact_form(request, form, ajax=False):
    """Shared logic: save message, send email, return response."""
    try:
        contact = form.save(commit=False)
        # Capture IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        contact.ip_address = (
            x_forwarded_for.split(',')[0] if x_forwarded_for
            else request.META.get('REMOTE_ADDR')
        )
        contact.save()

        # Send notification email
        _send_contact_notification(contact)

        logger.info('Contact message received from %s <%s>', contact.name, contact.email)

        if ajax:
            return JsonResponse({'success': True,
                                  'message': 'Message envoyé avec succès!'})
        messages.success(request, '✓ Votre message a été envoyé. Je vous répondrai sous peu.')
        return redirect('core:index')

    except Exception as exc:
        logger.error('Contact form error: %s', exc, exc_info=True)
        if ajax:
            return JsonResponse({'success': False,
                                  'message': 'Erreur serveur. Veuillez réessayer.'}, status=500)
        messages.error(request, 'Une erreur est survenue. Veuillez réessayer ou me contacter directement.')
        return redirect('core:index')


def _send_contact_notification(contact: ContactMessage):
    """Send admin notification email — fails silently if not configured."""
    try:
        subject = f'[Portfolio] Nouveau message: {contact.subject}'
        body = (
            f'Nom: {contact.name}\n'
            f'Courriel: {contact.email}\n'
            f'Sujet: {contact.subject}\n\n'
            f'Message:\n{contact.message}'
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,
        )
    except Exception as exc:
        logger.warning('Email notification failed: %s', exc)


# ── Error handlers ─────────────────────────────────────────────────────────────

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)

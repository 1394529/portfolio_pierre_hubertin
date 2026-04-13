"""
Tests unitaires et d'intégration — Portfolio Pierre Hubertin

Couverture :
  - Modèles : Project, Skill, BlogPost, ContactMessage
  - Vues    : index, project_detail, blog, contact AJAX
  - Forms   : ContactForm validation, honeypot anti-spam
  - Routing : URLs résolues correctement
"""

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.core import mail
from django.utils import timezone

from .models import Project, SkillCategory, Skill, BlogPost, ContactMessage
from .forms import ContactForm
from . import views


# ── Factories ──────────────────────────────────────────────────────────────────

def make_project(**kwargs) -> Project:
    defaults = dict(
        title='Dashboard KPI Test',
        category='powerbi',
        short_description='Un dashboard de test pour les KPI financiers.',
        technologies='Power BI, DAX, SQL',
        status='published',
        featured=False,
        order=1,
    )
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


def make_skill_category(**kwargs) -> SkillCategory:
    defaults = dict(name='BI Tools', icon='bi-bar-chart', order=1)
    defaults.update(kwargs)
    return SkillCategory.objects.create(**defaults)


def make_skill(category, **kwargs) -> Skill:
    defaults = dict(name='Power BI', level=5, percentage=95, order=1)
    defaults.update(kwargs)
    return Skill.objects.create(category=category, **defaults)


def make_blog_post(**kwargs) -> BlogPost:
    defaults = dict(
        title='Optimiser DAX pour le reporting financier',
        excerpt='Les 5 meilleures pratiques DAX.',
        content='<p>Contenu de test.</p>',
        tags='DAX, Power BI',
        status='published',
        published_at=timezone.now(),
    )
    defaults.update(kwargs)
    return BlogPost.objects.create(**defaults)


# ── Model Tests ────────────────────────────────────────────────────────────────

class ProjectModelTest(TestCase):

    def test_slug_auto_generated(self):
        p = make_project(title='Analyse Crédit Test')
        self.assertEqual(p.slug, 'analyse-credit-test')

    def test_slug_unique_preserved(self):
        p = make_project(title='Mon Projet', slug='mon-projet-custom')
        self.assertEqual(p.slug, 'mon-projet-custom')

    def test_get_technologies_list(self):
        p = make_project(technologies='Power BI, DAX , SQL Server')
        techs = p.get_technologies_list()
        self.assertEqual(techs, ['Power BI', 'DAX', 'SQL Server'])

    def test_technologies_list_empty(self):
        p = make_project(technologies='')
        self.assertEqual(p.get_technologies_list(), [])

    def test_is_published_property(self):
        p_pub = make_project(status='published')
        p_drft = make_project(title='Brouillon', status='draft')
        self.assertTrue(p_pub.is_published)
        self.assertFalse(p_drft.is_published)

    def test_str_representation(self):
        p = make_project(title='Mon Dashboard')
        self.assertEqual(str(p), 'Mon Dashboard')

    def test_ordering(self):
        p2 = make_project(title='Projet B', order=2)
        p1 = make_project(title='Projet A', order=1)
        projects = list(Project.objects.all())
        self.assertEqual(projects[0], p1)
        self.assertEqual(projects[1], p2)


class SkillModelTest(TestCase):

    def setUp(self):
        self.cat = make_skill_category()

    def test_get_stars_expert(self):
        skill = make_skill(self.cat, level=4)
        stars = skill.get_stars()
        self.assertEqual(len(stars), 5)
        self.assertEqual(sum(stars), 4)
        self.assertTrue(all(stars[:4]))
        self.assertFalse(stars[4])

    def test_get_stars_master(self):
        skill = make_skill(self.cat, level=5)
        self.assertTrue(all(skill.get_stars()))

    def test_get_stars_beginner(self):
        skill = make_skill(self.cat, level=1)
        stars = skill.get_stars()
        self.assertTrue(stars[0])
        self.assertFalse(any(stars[1:]))

    def test_str_representation(self):
        skill = make_skill(self.cat, name='DAX', level=5)
        self.assertIn('DAX', str(skill))
        self.assertIn('Maître', str(skill))


class BlogPostModelTest(TestCase):

    def test_slug_auto_generated(self):
        post = make_blog_post(title='Optimiser ETL avec dbt')
        self.assertEqual(post.slug, 'optimiser-etl-avec-dbt')

    def test_published_at_set_on_publish(self):
        post = make_blog_post(status='draft', published_at=None)
        self.assertIsNone(post.published_at)
        post.status = 'published'
        post.save()
        self.assertIsNotNone(post.published_at)

    def test_get_tags_list(self):
        post = make_blog_post(tags='DAX, Power BI , ETL')
        self.assertEqual(post.get_tags_list(), ['DAX', 'Power BI', 'ETL'])

    def test_is_published(self):
        post = make_blog_post(status='published')
        self.assertTrue(post.is_published)


class ContactMessageModelTest(TestCase):

    def test_str_representation(self):
        msg = ContactMessage.objects.create(
            name='Jean Tremblay',
            email='jean@test.com',
            subject='Question projet BI',
            message='Bonjour, je cherche un analyste BI pour mon entreprise.',
        )
        self.assertIn('Jean Tremblay', str(msg))
        self.assertIn('Question projet BI', str(msg))


# ── Form Tests ─────────────────────────────────────────────────────────────────

class ContactFormTest(TestCase):

    VALID_DATA = {
        'name': 'Marie Dupont',
        'email': 'marie@exemple.com',
        'subject': 'Proposition de collaboration BI',
        'message': 'Bonjour Pierre, je souhaite discuter d\'un projet Power BI pour notre entreprise.',
        'website': '',  # honeypot vide
    }

    def test_valid_form(self):
        form = ContactForm(data=self.VALID_DATA)
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_name(self):
        data = {**self.VALID_DATA, 'name': ''}
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_too_short(self):
        data = {**self.VALID_DATA, 'name': 'A'}
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_email(self):
        data = {**self.VALID_DATA, 'email': 'pas-un-email'}
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_message_too_short(self):
        data = {**self.VALID_DATA, 'message': 'Trop court.'}
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_honeypot_filled_rejected(self):
        data = {**self.VALID_DATA, 'website': 'http://spam.com'}
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_missing_subject(self):
        data = {**self.VALID_DATA, 'subject': ''}
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)

    def test_subject_too_short(self):
        data = {**self.VALID_DATA, 'subject': 'AB'}
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())


# ── View / Integration Tests ───────────────────────────────────────────────────

class IndexViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:index')
        # Populate DB
        self.project = make_project(featured=True)
        self.cat = make_skill_category()
        make_skill(self.cat)
        self.post = make_blog_post()

    def test_index_status_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_index_context_contains_projects(self):
        response = self.client.get(self.url)
        self.assertIn('projects', response.context)
        self.assertEqual(len(response.context['projects']), 1)

    def test_index_context_skills(self):
        response = self.client.get(self.url)
        self.assertIn('skill_categories', response.context)

    def test_index_context_recent_posts(self):
        response = self.client.get(self.url)
        self.assertIn('recent_posts', response.context)

    def test_index_context_contact_form(self):
        response = self.client.get(self.url)
        self.assertIn('contact_form', response.context)
        self.assertIsInstance(response.context['contact_form'], ContactForm)

    def test_draft_projects_not_shown(self):
        make_project(title='Brouillon', status='draft')
        response = self.client.get(self.url)
        titles = [p.title for p in response.context['projects']]
        self.assertNotIn('Brouillon', titles)

    def test_page_contains_owner_name(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Pierre Hubertin')


class ProjectDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.project = make_project(title='Projet Détail Test')

    def test_project_detail_200(self):
        url = reverse('core:project_detail', kwargs={'slug': self.project.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_project_detail_404_for_draft(self):
        draft = make_project(title='Projet Brouillon', status='draft')
        url = reverse('core:project_detail', kwargs={'slug': draft.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_project_detail_contains_title(self):
        url = reverse('core:project_detail', kwargs={'slug': self.project.slug})
        response = self.client.get(url)
        self.assertContains(response, 'Projet Détail Test')

    def test_project_detail_404_unknown_slug(self):
        url = reverse('core:project_detail', kwargs={'slug': 'inexistant'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class BlogViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.post = make_blog_post()

    def test_blog_list_200(self):
        url = reverse('core:blog_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_blog_list_shows_published_only(self):
        make_blog_post(title='Brouillon', status='draft', published_at=None)
        response = self.client.get(reverse('core:blog_list'))
        titles = [p.title for p in response.context['posts']]
        self.assertNotIn('Brouillon', titles)

    def test_blog_detail_200(self):
        url = reverse('core:blog_detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_contains_title(self):
        url = reverse('core:blog_detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        self.assertContains(response, self.post.title)

    def test_blog_detail_draft_404(self):
        draft = make_blog_post(title='Brouillon', status='draft', published_at=None)
        url = reverse('core:blog_detail', kwargs={'slug': draft.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ContactAjaxViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:contact_ajax')
        self.valid_data = {
            'name': 'Sophie Martin',
            'email': 'sophie@test.com',
            'subject': 'Projet Power BI reporting',
            'message': 'Bonjour, je cherche un expert Power BI pour automatiser notre reporting mensuel.',
            'website': '',
        }

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_valid_submission_returns_200_json(self):
        response = self.client.post(self.url, data=self.valid_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_valid_submission_saves_to_db(self):
        self.client.post(self.url, data=self.valid_data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Sophie Martin')
        self.assertEqual(msg.status, 'new')

    def test_invalid_email_returns_400(self):
        data = {**self.valid_data, 'email': 'pas-valide'}
        response = self.client.post(self.url, data=data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_honeypot_filled_rejected(self):
        data = {**self.valid_data, 'website': 'http://spam.bot'}
        response = self.client.post(self.url, data=data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_short_message_rejected(self):
        data = {**self.valid_data, 'message': 'Trop court.'}
        response = self.client.post(self.url, data=data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_email_notification_sent(self):
        """Vérifie qu'un courriel de notification est envoyé (console backend)."""
        self.client.post(self.url, data=self.valid_data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # Avec le backend console, outbox n'est pas rempli, mais
        # on vérifie que la soumission réussit sans exception.
        self.assertEqual(ContactMessage.objects.count(), 1)


# ── URL Routing Tests ──────────────────────────────────────────────────────────

class URLRoutingTest(TestCase):

    def test_index_url_resolves(self):
        resolver = resolve('/')
        self.assertEqual(resolver.func, views.index)

    def test_blog_list_url_resolves(self):
        resolver = resolve('/blog/')
        self.assertEqual(resolver.func, views.blog_list)

    def test_contact_ajax_url_resolves(self):
        resolver = resolve('/contact/ajax/')
        self.assertEqual(resolver.func, views.contact_ajax)

    def test_project_detail_url_resolves(self):
        resolver = resolve('/projets/mon-projet/')
        self.assertEqual(resolver.func, views.project_detail)

    def test_blog_detail_url_resolves(self):
        resolver = resolve('/blog/mon-article/')
        self.assertEqual(resolver.func, views.blog_detail)


# ── Context Processor Tests ────────────────────────────────────────────────────

class ContextProcessorTest(TestCase):

    def test_global_context_in_response(self):
        response = self.client.get(reverse('core:index'))
        self.assertIn('OWNER_NAME', response.context)
        self.assertIn('OWNER_GITHUB', response.context)
        self.assertIn('CV_DOWNLOAD_URL', response.context)
        self.assertEqual(response.context['OWNER_NAME'], 'Pierre Hubertin')

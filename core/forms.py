"""
Forms for the portfolio — contact form with server-side validation.
"""

from django import forms
from django.core.exceptions import ValidationError
import re

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form with honeypot anti-spam and validation."""

    # Honeypot field — hidden from real users, filled by bots
    website = forms.CharField(required=False, widget=forms.HiddenInput, label='')

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet',
                'autocomplete': 'name',
                'aria-label': 'Nom complet',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com',
                'autocomplete': 'email',
                'aria-label': 'Adresse courriel',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet de votre message',
                'aria-label': 'Sujet',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Décrivez votre projet, votre besoin ou votre question...',
                'aria-label': 'Message',
            }),
        }
        labels = {
            'name': 'Nom complet',
            'email': 'Courriel',
            'subject': 'Sujet',
            'message': 'Message',
        }
        error_messages = {
            'name': {'required': 'Veuillez entrer votre nom.'},
            'email': {
                'required': 'Veuillez entrer votre adresse courriel.',
                'invalid': 'Format de courriel invalide.',
            },
            'subject': {'required': 'Veuillez indiquer un sujet.'},
            'message': {'required': 'Veuillez rédiger votre message.'},
        }

    def clean_website(self):
        """Honeypot: reject if filled."""
        value = self.cleaned_data.get('website', '')
        if value:
            raise ValidationError('Soumission rejetée (spam détecté).')
        return value

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise ValidationError('Le nom doit contenir au moins 2 caractères.')
        if len(name) > 200:
            raise ValidationError('Le nom ne peut dépasser 200 caractères.')
        return name

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 20:
            raise ValidationError('Le message doit contenir au moins 20 caractères.')
        if len(message) > 5000:
            raise ValidationError('Le message ne peut dépasser 5 000 caractères.')
        return message

    def clean_subject(self):
        subject = self.cleaned_data.get('subject', '').strip()
        if len(subject) < 3:
            raise ValidationError('Le sujet doit contenir au moins 3 caractères.')
        return subject

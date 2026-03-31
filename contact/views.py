import logging

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.contrib import messages


logger = logging.getLogger(__name__)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            full_message = f"From: {name} <{email}>\n\n{message}"

            try:
                send_mail(
                    subject,
                    full_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
            except Exception:
                logger.exception("Contact form email send failed.")
                messages.error(request, "Unable to send message right now. Please try again later.")
                return render(request, 'contact/contact.html', {'form': form})

            messages.success(request, "Thank you for contacting us. We will get back to you soon!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})

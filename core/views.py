"""
Views for core app (public pages).
"""
from django.shortcuts import render
from django.contrib import messages
from .forms import ContactForm


def home(request):
    """
    Display the homepage with track information and recent sessions.
    """
    from sessions.models import SessionSlot
    from django.utils import timezone

    # Get upcoming sessions (next 5)
    upcoming_sessions = SessionSlot.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:5]

    context = {
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    Display the about page with track information and facility details.
    """
    from sessions.models import Track

    # Get track information (single venue)
    track = Track.objects.first()

    context = {
        'track': track,
    }
    return render(request, 'core/about.html', context)


def contact(request):
    """
    Display and process the contact form.
    Sends email on successful submission (console backend in dev).
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']

            # Send email (will output to console in development)
            from django.core.mail import send_mail
            full_message = f"From: {name} <{email}>\n\n{message_body}"

            try:
                send_mail(
                    subject=f"KartControl Contact: {subject}",
                    message=full_message,
                    from_email=email,
                    recipient_list=['info@kartcontrol.com'],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    'Thank you for your message! We will get back to you soon.'
                )
                # Redirect to prevent form resubmission
                from django.shortcuts import redirect
                return redirect('core:contact')
            except Exception as e:
                messages.error(
                    request,
                    'Sorry, there was an error sending your message. Please try again later.'
                )
    else:
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request, 'core/contact.html', context)

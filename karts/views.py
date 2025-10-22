"""
Views for karts app (kart management).
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Kart
from .forms import KartForm


def is_manager(user):
    """Check if user has manager role."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_manager()


@login_required
@user_passes_test(is_manager)
def kart_list(request):
    """
    Display list of all karts.
    Manager-only view.
    """
    karts = Kart.objects.all().order_by('number')

    context = {
        'karts': karts,
    }
    return render(request, 'karts/kart_list.html', context)


@login_required
@user_passes_test(is_manager)
def kart_create(request):
    """
    Create a new kart.
    Manager-only view with form validation.
    """
    if request.method == 'POST':
        form = KartForm(request.POST)
        if form.is_valid():
            kart = form.save()
            messages.success(
                request,
                f'Kart #{kart.number} has been created successfully.'
            )
            return redirect('karts:kart_list')
    else:
        form = KartForm()

    context = {
        'form': form,
        'title': 'Add New Kart',
    }
    return render(request, 'karts/kart_form.html', context)

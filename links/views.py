from django.contrib import messages
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ShortLinkForm
from .models import ShortLink


def home(request: HttpRequest) -> HttpResponse:
    form = ShortLinkForm(request.POST or None)
    created_link = None

    if request.method == "POST":
        if form.is_valid():
            created_link = form.save()
            messages.success(
                request,
                "Short URL created successfully! Copy the link below to share it.",
            )
            form = ShortLinkForm()
        else:
            messages.error(request, "Please review the form and fix the highlighted fields.")

    latest_links = ShortLink.objects.all()[:10]
    full_short_url = None
    base_short_url = request.build_absolute_uri("/").rstrip("/")
    if created_link:
        full_short_url = f"{base_short_url}{reverse('links:redirect', args=[created_link.short_code])}"

    context = {
        "form": form,
        "created_link": created_link,
        "full_short_url": full_short_url,
        "latest_links": latest_links,
        "base_short_url": base_short_url,
    }
    return render(request, "links/home.html", context)


def redirect_short_link(request: HttpRequest, short_code: str) -> HttpResponse:
    short_link = get_object_or_404(ShortLink, short_code__iexact=short_code)
    ShortLink.objects.filter(pk=short_link.pk).update(click_count=F("click_count") + 1)
    return redirect(short_link.original_url)

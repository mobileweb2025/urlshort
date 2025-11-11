from django.contrib import messages
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AliasUpdateForm, ShortLinkForm
from .models import ShortLink


def home(request: HttpRequest) -> HttpResponse:
    created_link = None
    full_short_url = None
    base_short_url = request.build_absolute_uri("/").rstrip("/")

    last_link_id = request.session.get("last_shortlink_id")
    if last_link_id:
        created_link = ShortLink.objects.filter(pk=last_link_id).first()
        if created_link is None:
            request.session.pop("last_shortlink_id", None)

    create_form = ShortLinkForm()
    alias_form = None

    if created_link:
        full_short_url = f"{base_short_url}{reverse('links:redirect', args=[created_link.short_code])}"
        alias_form = AliasUpdateForm(
            initial={"link_id": created_link.pk, "new_alias": created_link.short_code}
        )

    if request.method == "POST":
        action = request.POST.get("action", "create")
        if action == "create":
            create_form = ShortLinkForm(request.POST)
            if create_form.is_valid():
                created_link = create_form.save()
                request.session["last_shortlink_id"] = created_link.pk
                full_short_url = f"{base_short_url}{reverse('links:redirect', args=[created_link.short_code])}"
                alias_form = AliasUpdateForm(
                    initial={
                        "link_id": created_link.pk,
                        "new_alias": created_link.short_code,
                    }
                )
                messages.success(
                    request,
                    "Short URL created successfully! Copy or customize the link below.",
                )
                create_form = ShortLinkForm()
            else:
                messages.error(
                    request,
                    "Please review the form and fix the highlighted fields.",
                )
        elif action == "update":
            alias_form = AliasUpdateForm(request.POST)
            if alias_form.is_valid():
                link_id = alias_form.cleaned_data["link_id"]
                short_link = get_object_or_404(ShortLink, pk=link_id)
                new_alias = alias_form.cleaned_data["new_alias"]
                short_link.short_code = new_alias
                short_link.save(update_fields=["short_code", "updated_at"])
                request.session["last_shortlink_id"] = short_link.pk
                created_link = short_link
                full_short_url = f"{base_short_url}{reverse('links:redirect', args=[short_link.short_code])}"
                alias_form = AliasUpdateForm(
                    initial={
                        "link_id": short_link.pk,
                        "new_alias": short_link.short_code,
                    }
                )
                messages.success(request, "Alias updated successfully.")
            else:
                messages.error(
                    request,
                    "The alias could not be updated. Please fix the highlighted field.",
                )
                link_id = request.POST.get("link_id")
                if link_id:
                    created_link = ShortLink.objects.filter(pk=link_id).first()
                    if created_link:
                        full_short_url = f"{base_short_url}{reverse('links:redirect', args=[created_link.short_code])}"

    context = {
        "form": create_form,
        "created_link": created_link,
        "full_short_url": full_short_url,
        "alias_form": alias_form,
    }
    return render(request, "links/home.html", context)


def redirect_short_link(request: HttpRequest, short_code: str) -> HttpResponse:
    short_link = get_object_or_404(ShortLink, short_code__iexact=short_code)
    ShortLink.objects.filter(pk=short_link.pk).update(click_count=F("click_count") + 1)
    return redirect(short_link.original_url)

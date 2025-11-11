from django import forms
from django.utils.text import slugify

from .models import ShortLink


class ShortLinkForm(forms.ModelForm):
    custom_alias = forms.CharField(
        max_length=20,
        required=False,
        help_text="Optional: provide your own short name (letters, numbers, hyphen).",
        label="Custom short name (optional)",
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. holiday-sale",
                "class": "input-control",
            }
        ),
    )

    class Meta:
        model = ShortLink
        fields = ("original_url", "custom_alias")
        widgets = {
            "original_url": forms.URLInput(
                attrs={
                    "placeholder": "Paste your long URL here",
                    "class": "input-control",
                }
            ),
        }
        labels = {"original_url": "Original URL"}

    def clean_custom_alias(self) -> str:
        alias = self.cleaned_data.get("custom_alias", "").strip()
        if not alias:
            return ""

        normalized = slugify(alias)
        if len(normalized) < 3:
            raise forms.ValidationError("Custom name must be at least 3 characters after normalization.")

        if ShortLink.objects.filter(short_code__iexact=normalized).exists():
            raise forms.ValidationError("This custom name is already taken. Please try another one.")

        return normalized

    def save(self, commit: bool = True) -> ShortLink:
        instance = super().save(commit=False)
        alias = self.cleaned_data.get("custom_alias")
        instance.short_code = alias or ShortLink.generate_unique_code()
        if commit:
            instance.save()
        return instance


class AliasUpdateForm(forms.Form):
    link_id = forms.IntegerField(widget=forms.HiddenInput())
    new_alias = forms.CharField(
        max_length=20,
        label="Edit short name",
        help_text="Update the alias as long as it is unique.",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Type a new alias",
                "class": "input-control",
            }
        ),
    )

    def clean_new_alias(self) -> str:
        alias = self.cleaned_data.get("new_alias", "").strip()
        if not alias:
            raise forms.ValidationError("Alias cannot be empty.")

        normalized = slugify(alias)
        if len(normalized) < 3:
            raise forms.ValidationError(
                "Custom name must be at least 3 characters after normalization."
            )
        self.cleaned_data["new_alias"] = normalized
        return normalized

    def clean(self):
        cleaned_data = super().clean()
        alias = cleaned_data.get("new_alias")
        link_id = cleaned_data.get("link_id")
        if alias and link_id:
            if ShortLink.objects.exclude(pk=link_id).filter(
                short_code__iexact=alias
            ).exists():
                self.add_error(
                    "new_alias",
                    "This custom name is already taken. Please try another one.",
                )
        return cleaned_data

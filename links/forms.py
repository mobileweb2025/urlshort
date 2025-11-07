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
                "class": "input",
            }
        ),
    )

    class Meta:
        model = ShortLink
        fields = ("original_url", "custom_alias")
        widgets = {
            "original_url": forms.URLInput(
                attrs={"placeholder": "Paste your long URL here", "class": "input"}
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

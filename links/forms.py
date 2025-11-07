from django import forms
from django.utils.text import slugify

from .models import ShortLink


class ShortLinkForm(forms.ModelForm):
    custom_alias = forms.CharField(
        max_length=20,
        required=False,
        help_text="Opsional: masukkan nama pendek sendiri (huruf, angka, tanda hubung).",
        label="Nama pendek (opsional)",
        widget=forms.TextInput(
            attrs={
                "placeholder": "contoh: promo-akhir-tahun",
                "class": "input",
            }
        ),
    )

    class Meta:
        model = ShortLink
        fields = ("original_url", "custom_alias")
        widgets = {
            "original_url": forms.URLInput(
                attrs={"placeholder": "Tempel URL panjang di sini", "class": "input"}
            ),
        }
        labels = {"original_url": "URL asli"}

    def clean_custom_alias(self) -> str:
        alias = self.cleaned_data.get("custom_alias", "").strip()
        if not alias:
            return ""

        normalized = slugify(alias)
        if len(normalized) < 3:
            raise forms.ValidationError("Nama pendek minimal 3 karakter setelah dinormalisasi.")

        if ShortLink.objects.filter(short_code__iexact=normalized).exists():
            raise forms.ValidationError("Nama pendek sudah dipakai. Silakan coba nama lain.")

        return normalized

    def save(self, commit: bool = True) -> ShortLink:
        instance = super().save(commit=False)
        alias = self.cleaned_data.get("custom_alias")
        instance.short_code = alias or ShortLink.generate_unique_code()
        if commit:
            instance.save()
        return instance

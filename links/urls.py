from django.urls import path

from . import views

app_name = "links"

urlpatterns = [
    path("", views.home, name="home"),
    path("<str:short_code>/", views.redirect_short_link, name="redirect"),
]

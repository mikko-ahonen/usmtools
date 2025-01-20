from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView 

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('', RedirectView.as_view(url='/workflows/')),
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico')),
    path('admin/', admin.site.urls),
    #path('public/', include('public.urls')),
    #path('webmention/', include('webmention.urls')),
    path('workflows/', include('workflows.urls')),
    path('mir/', include('mir.urls')),
    path('xref/', include('xref.urls')),
    #path("accounts/", include("django.contrib.auth.urls")),
    #path('i18n/', include('django.conf.urls.i18n')),
    path('sentry-debug/', trigger_error),
    path('accounts/', include('accounts.urls')),
    #path('survey/', include('survey.urls')),
    path('compliances/', include('compliances.urls')),
    path('boards/', include('boards.urls')),
    path('projects/', include('projects.urls')),
    path('components/', include('components.urls')),
    path("", include("django_components.urls")),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

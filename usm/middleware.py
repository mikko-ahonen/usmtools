import re
import functools

from django.conf import settings
from django.utils import translation
from django.utils import timezone

from django.utils import translation
from workflows.tenant import set_tenant_id
from workflows.models import Tenant

class SetTenantMiddleware:

    def __init__(self, process_request):
        self.process_request = process_request

    def __call__(self, request):
        path = request.get_full_path()
        m = re.search(r'^/(?:workflows|compliances|boards|projects)/(?:tenants/)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/', path)
        if m:
            tenant_id = m.group(1)
            tenant = Tenant.objects.get(id=tenant_id)
            user = request.user
            if request.user.is_superuser or tenant.owner == request.user:
                set_tenant_id(tenant_id)
        response = self.process_request(request)
        return response

class AdminLocaleMiddleware:
    def __init__(self, process_request):
        self.process_request = process_request

    def __call__(self, request):

        if request.path.startswith('/admin'):
            translation.activate("en")
            request.LANGUAGE_CODE = translation.get_language()

        response = self.process_request(request)

        return response

class LastSeenMiddleware(object):
    """
    Simple middleware to set last_seen_on and last_activity_ip on user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            user.last_seen_on = timezone.now()
            user.last_activity_ip = request.META['REMOTE_ADDR']
            user.save()
        response = self.get_response(request)
        return response

@functools.lru_cache()
def get_languages():
    """
    Cache of settings.LANGUAGES in a dictionary for easy lookups by key.
    """
    return dict(settings.LANGUAGES)

class ProfileLocaleMiddleware:
    """
    Simple LocaleMiddleware replacement that uses the lang attribute in the user profile and session cookies to set language.
    """


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        cookie_name = settings.LANGUAGE_COOKIE_NAME
        cookie_domain = settings.LANGUAGE_COOKIE_DOMAIN
        cookie_age = settings.LANGUAGE_COOKIE_AGE

        set_cookie = False

        lang = request.COOKIES.get(cookie_name)

        if lang is None:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                lang = user.lang
                set_cookie = True

        if lang is None:
            lang = translation.get_language_from_request(request)

        if lang is not None and lang in get_languages() and translation.check_for_language(lang):
            translation.activate(lang)
            request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)

        if set_cookie:
            response.set_cookie(cookie_name,
                                lang,
                                max_age=cookie_age,
                                domain=cookie_domain)

        response.setdefault('Content-Language', lang) 

        #if 'Content-Language' not in response:
        #    response['Content-Language'] = lang
        return response


from django.shortcuts import render

from django.views import View

from django.utils.translation import activate
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.utils.encoding import iri_to_uri, force_str
from django.http import HttpResponseRedirect
from django.conf import settings

def get_url_with_next_url(url, next_url):
    if not next_url:
        return url
    params = urlencode({'next': next_url})
    if '?' not in url:
        return url + '?' + params
    return url + '&' + params

def make_next_url_safe(url):
    if url and url_has_allowed_host_and_scheme(url, None): # None means: host not allowed
        url = iri_to_uri(url)
        return url
    return "/public/"

class SetLangView(View):
    def get(self, request, lang, *args, **kwargs):
        if lang not in ['fi', 'en']:
            raise ValueError("Only fi and en are supported. Vain kielet fi ja en tuettu.")
        activate(lang)
        next_url = make_next_url_safe(self.request.GET.get('next', None))
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response

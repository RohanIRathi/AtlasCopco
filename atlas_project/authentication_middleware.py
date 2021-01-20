from django.contrib import auth
from django.contrib.auth.middleware import MiddlewareMixin, get_user
from django.http import HttpResponseForbidden
from django.utils.functional import SimpleLazyObject


class AutomaticUserLoginMiddleware(MiddlewareMixin):

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: get_user(request))

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not self._is_user_authenticated(request):
            user = auth.authenticate(request)
            if user is None:
                return HttpResponseForbidden('403')

            request.user = user
            auth.login(request, user)

    @staticmethod
    def _is_user_authenticated(request):
        user = request.user
        return user and user.is_authenticated
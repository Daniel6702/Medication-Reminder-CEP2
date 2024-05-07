from django.contrib.auth import login
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User

class ImpersonateMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_superuser and 'impersonate_id' in request.session:
            try:
                user_id = request.session['impersonate_id']
                user = User.objects.get(pk=user_id)
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # important for manual login
                login(request, user)
            except User.DoesNotExist:
                del request.session['impersonate_id']  # cleanup session if user doesn't exist

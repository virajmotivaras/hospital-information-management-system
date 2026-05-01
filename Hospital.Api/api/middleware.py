from django.shortcuts import redirect


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        allowed_paths = (
            "/login/",
            "/logout/",
            "/change-password/",
            "/static/",
            "/media/",
        )
        if user.is_authenticated and not request.path.startswith(allowed_paths):
            profile = getattr(user, "staff_profile", None)
            if profile and profile.must_change_password:
                return redirect("/change-password/")

        return self.get_response(request)

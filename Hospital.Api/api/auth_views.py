from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

from repository.models import StaffProfile


@csrf_protect
def app_login(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            profile = StaffProfile.objects.filter(user=user).first()
            if profile and profile.must_change_password:
                return redirect("/change-password/")
            return redirect("/")
        error = "Invalid username or password."

    return render(request, "login.html", {"error": error})


@login_required
@csrf_protect
def force_password_change(request):
    profile, _created = StaffProfile.objects.get_or_create(user=request.user)
    error = ""

    if request.method == "POST":
        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not request.user.check_password(current_password):
            error = "Current password is incorrect."
        elif len(new_password) < 8:
            error = "New password must be at least 8 characters."
        elif new_password != confirm_password:
            error = "New passwords do not match."
        else:
            request.user.set_password(new_password)
            request.user.save()
            profile.must_change_password = False
            profile.save(update_fields=["must_change_password"])
            update_session_auth_hash(request, request.user)
            return redirect("/")

    return render(
        request,
        "change_password.html",
        {"error": error, "must_change_password": profile.must_change_password},
    )

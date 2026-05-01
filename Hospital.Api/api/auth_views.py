from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def app_login(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")
        error = "Invalid username or password."

    return render(request, "login.html", {"error": error})

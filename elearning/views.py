from django.shortcuts import render


def csrf_failure(request, reason="", template_name="403_csrf.html"):
    response = render(
        request,
        template_name,
        {
            "reason": reason,
        },
        status=403,
    )
    return response


def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)


def custom_server_error(request):
    return render(request, "500.html", status=500)

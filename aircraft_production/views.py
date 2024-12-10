from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)

def test_500(request):
    # This will raise an error and trigger the 500 error page
    raise Exception("Test 500 error")

def test_403(request):
    # This will raise a 403 error
    raise PermissionDenied("Test 403 error")
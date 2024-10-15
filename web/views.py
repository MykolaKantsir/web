from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Generate CSRF token
            csrf_token = get_token(request)
            return JsonResponse({'status': 'success', 'csrf_token': csrf_token})
        else:
            return JsonResponse({'status': 'failed', 'error': 'Invalid credentials'})
    
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return HttpResponse("Logged out successfully")  # Redirect to the login page or any desired page after logout

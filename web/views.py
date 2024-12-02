from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.urls import reverse


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # If the request is an AJAX request, return JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Generate CSRF token
                csrf_token = get_token(request)
                return JsonResponse({'status': 'success', 'csrf_token': csrf_token})
            else:
                # Handle regular form submission and redirect to the next page
                next_url = request.GET.get('next', reverse('dashboard'))  # Use 'dashboard' as the name of your desired URL
                return HttpResponseRedirect(next_url)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'failed', 'error': 'Invalid credentials'})
            else:
                # Return login page with error message for regular requests
                return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    
    # Render the login page for GET requests
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return HttpResponse("Logged out successfully")  # Redirect to the login page or any desired page after logout

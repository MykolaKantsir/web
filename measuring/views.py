from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'measuring/index_content.html')

# Add new template view
def new_template(request):
    return render(request, 'measuring/new_template.html')

# Measure view
def measure(request):
    return render(request, 'measuring/measure.html')
from django.shortcuts import render
from django.http import JsonResponse


def index(request):
    """Main webshop view"""
    context = {
        'title': 'Webshop',
        'description': 'Browse our products',
    }
    return render(request, 'webshop/index.html', context)


def products(request):
    """Products listing view"""
    context = {
        'title': 'Products',
        'products': [],  # TODO: Fetch from database
    }
    return render(request, 'webshop/products.html', context)


def api_products_list(request):
    """API endpoint for listing products"""
    # TODO: Implement actual product listing logic
    products = [
        {'id': 1, 'name': 'Product 1', 'price': 19.99},
        {'id': 2, 'name': 'Product 2', 'price': 29.99},
    ]
    return JsonResponse({'products': products})

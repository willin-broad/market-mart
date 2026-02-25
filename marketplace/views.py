from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from payments.models import Seller_Account
from marketplace.models import Product

@login_required
def create_product(request):
    return render(request, 'create_product.html')

@login_required
def post_product(request):
    if request.method == "POST":
        product_name = request.POST['product_name']
        price = request.POST['price']
        product_description = request.POST['product_description']
        product_image = request.FILES.get('product_image')

        # Create a new post and associate it with the current logged-in user
        product = Product(
            product_name=product_name,
            price = price,
            product_description=product_description,
            product_image=product_image,
            user=request.user  
        )
        product.save()

        Seller_Account.objects.get_or_create(
            user=request.user,
            
        )


        return redirect('marketplace')  
    return render(request, 'create_product.html')

@login_required
def marketplace(request):
    products = Product.objects.all()
    return render(request, 'marketplace.html', {"products": products})

@login_required
def myproducts(request):
    products = Product.objects.all()
    return render(request, 'my_products.html', {"products": products})

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the logged-in user is the owner of the product
    if product.user != request.user:
        return HttpResponseForbidden("You are not allowed to update this product.")

    if request.method == "POST":
        product.product_name = request.POST['product_name']
        product.product_description = request.POST['product_description']
        if 'product_image' in request.FILES:
            product.product_image = request.FILES['product_image']
        product.save()
        return redirect('marketplace')

    return render(request, 'update_product.html', {'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the logged-in user is the owner of the product
    if product.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this product.")

    if request.method == "POST":
        product.delete()
        return redirect('marketplace')

    return render(request, 'delete_product.html', {'product': product})


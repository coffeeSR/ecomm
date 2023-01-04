from django.shortcuts import render,redirect
from django.views.generic.detail import View
from .models import *
from django.contrib.auth.models import  User
from django.contrib import messages

# Create your views here.
class BaseView(View):
    views={}
    views['categories'] = Category.objects.all()
    views['brands'] = Brand.objects.all()
    views['sale_products'] = Product.objects.filter(label='sale', stock='In stock')

class HomeView(BaseView):
    def get(self,request):
        self.views['sliders']=Slider.objects.all()
        self.views['ads']=Ad.objects.all()
        self.views['new_products']=Product.objects.filter(label='new',stock='In stock')
        self.views['hot_products']=Product.objects.filter(label='hot',stock='In stock')

        return render(request,'index.html',self.views)

class CategoryView(BaseView):
    def get(self,request,slug):
        ids=Category.objects.get(slug=slug).id
        cat_name = Category.objects.get(slug=slug).name
        print(cat_name,ids)
        self.views['cat_product']=Product.objects.filter(category_id=ids)
        print(self.views['cat_product'])

        return render(request, 'category.html', self.views)

class BrandView(BaseView):
    def get(self,request,slug):
        ids=Brand.objects.get(slug=slug).id
        brand_name = Brand.objects.get(slug=slug).name
        print(brand_name,ids)
        self.views['brand_product']=Product.objects.filter(brand_id=ids)
        print(self.views['brand_product'])

        return render(request, 'brand.html', self.views)

class SearchView(BaseView):
    def get(self, request):
        query=request.GET.get('query')
        if query!='':
            self.views['search_product']=Product.objects.filter(name__icontains=query)
        else:
            return redirect('/')
        return render(request, 'search.html', self.views)

class ProductDetailView(BaseView):
    def get(self,request,slug):
        self.views['product_detail']=Product.objects.filter(slug=slug)
        subcat_id=Product.objects.get(slug=slug).subcategory_id
        product_id=Product.objects.get(slug=slug).id
        self.views['product_image'] = ProductImage.objects.filter(product_id=product_id)
        self.views['subcat_product'] = Product.objects.filter(subcategory_id=subcat_id)
        self.views['product_review']=ProductReview.objects.filter(slug=slug)
        return render(request, 'product-detail.html',self.views)

def signup(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        if password==cpassword:
            if User.objects.filter(username=username).exists():
                messages.error(request,'The username is already taken!')
                return redirect('/signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request,'The email is already taken!')
                return redirect('/signup')
            else:
                data=User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                data.save()
                # username = authenticate(username=username, password=password)
                return redirect('/accounts.login')
        else:
            messages.error(request,"Password doesn't match!")
            # username = authenticate(username=username, password=password)
            # login(request, user)
            # return redirect('/')
            return redirect('/signup')

    return render(request,'signup.html')

import datetime
def product_review(request,slug):
    if request.method == "POST":
        username=request.user.username
        email=request.user.email
        comment=request.POST['comment']
        star=request.POST['star']
        x=datetime.datetime.now()
        date=str(x.strftime('%c'))
        data=ProductReview.objects.create(
            username=username,
            email=email,
            comment=comment,
            star=star,
            date=date,
            slug=slug
        )
        data.save()

    return redirect(f"/details/{slug}")

def cart(request,slug):
    username=request.user.username
    if Cart.objects.filter(slug=slug,username=username,checkout=False).exists():
        quantity=Cart.objects.get(slug=slug,username=username,checkout=False).quantity
        price = Product.objects.get(slug=slug).price
        discounted_price = Product.objects.get(slug=slug).discounted_price
        quantity=quantity+1
        if discounted_price>0:
            original_price=quantity*discounted_price
        else:
            original_price = quantity * price
        Cart.objects.filter(slug=slug, username=username, checkout=False).update(quantity=quantity,total=original_price)
        return redirect('/my_cart')
    else:
        price = Product.objects.get(slug=slug).price
        discounted_price = Product.objects.get(slug=slug).discounted_price
        if discounted_price > 0:
            original_price = discounted_price
        else:
            original_price = price
        data=Cart.objects.create(
            username=username,
            slug=slug,
            total=original_price,
            items=Product.objects.filter(slug=slug)[0]
        )
        data.save()
        return redirect('/my_cart')

class CartView(BaseView):
    def get(self,request):
        grand_total=0
        username=request.user.username
        self.views['my_carts']=Cart.objects.filter(username=username, checkout=False)
        for i in self.views['my_carts']:
            grand_total=grand_total + i.total
        self.views['all_total']=grand_total
        self.views['shipping']=50
        self.views['grand_total']=grand_total+50
        return render(request,'cart.html',self.views)

def decrease_quantity(request,slug):
    username = request.user.username
    if Cart.objects.filter(slug=slug, username=username, checkout=False).exists():
        quantity = Cart.objects.get(slug=slug, username=username, checkout=False).quantity
        price = Product.objects.get(slug=slug).price
        discounted_price = Product.objects.get(slug=slug).discounted_price
        if quantity > 1:
            quantity = quantity - 1
            if discounted_price > 0:
                original_price = quantity * discounted_price
            else:
                original_price = quantity * price
            Cart.objects.filter(slug=slug, username=username, checkout=False).update(quantity=quantity,total=original_price)
            return redirect('/my_cart')
        else:
            messages.error(request, "Quantity cannot be less than 1!")
            return redirect('/my_cart')

def delete_cart(request,slug):
    username=request.user.username
    Cart.objects.filter(slug=slug, username=username, checkout=False).delete()
    return redirect('/my_cart')
    messages.error(request, "The Cart is removed!")
    return redirect('/my_cart')
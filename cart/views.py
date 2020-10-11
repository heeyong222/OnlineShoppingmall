from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
# Create your views here.

from shop.models import Product
from coupon.forms import AddCouponForm
from .forms import AddProductForm
from .cart import Cart

# 장바구니에 추가
@require_POST
def add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # 클라이언트 -> 서버로 데이터를 전달
    # 유효성 검사, injection 전처리
    # form = 회원가입, 로그인, pw 등과 같이 사용자로부터 입력받는것 처리방법
    form = AddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], is_update=cd['is_update'])
    # 추가 되었다면 detail창으로 연결
    return redirect('cart:detail')

def remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    # 삭제 되었으면 detail창으로 연결
    return redirect('cart:detail')

def detail(request):
    cart = Cart(request)
    add_coupon = AddCouponForm()
    for product in cart:
        product['quantity_form'] = AddProductForm(initial={'quantity':product['quantity'], 'is_update':True})

    return render(request, 'cart/detail.html', {'cart':cart,
                                                'add_coupon':add_coupon
                                                })
from django.shortcuts import render, get_object_or_404
from .models import *
from cart.cart import Cart
from .forms import *
# Create your views here.
# 함수형 view : request인자 필수
# 자바스크립트가 동작하지 않는 환경에서 주문을 하기위해
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        # 입력받은 정보를 후처리
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            # 쿠폰이 있는 경우
            if cart.coupon:
                order.coupon = cart.coupon
                #order.discount = cart.coupon.amount
                order.discount = cart.get_discount_total()
                order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            # 주문이 들어갔으니 장바구니 clear
            cart.clear()
            return render(request, 'order/created.html', {'order':order})
    else:
        # 주문자 정보를 입력받는 페이지
        form = OrderCreateForm()
    # 사용자가 정보 입력을 잘못 했을경우(form이 valid하지않은경우)를 대비해서 if문 밖에 render
    return render(request, 'order/create.html', {'cart':cart, 'form':form})


def order_complete(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/created.html', {'order':order})

from django.views.generic.base import View
from django.http import JsonResponse
# 자바스크립트가 동작하는경우
class OrderCreateAjaxView(View):
    def post(self, request, *args, **kwargs):
        # 로그인 하지 않았을때
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        cart = Cart(request)
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.get_discount_total()
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            data = {
                "order_id":order.id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)
# transaction 생성
class OrderCheckoutAjaxView(View):
    def post(self, request, *args, **kwargs):
        # 로그인을 하지 않은 경우
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated": False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        amount = request.POST.get('amount')

        try:
            merchant_order_id = OrderTransaction.objects.create_new(
                order=order,
                amount=amount
            )
        except:
            # 실패한경우
            merchant_order_id = None

        if merchant_order_id is not None:
            data = {
                "works":True,
                "merchant_id":merchant_order_id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)
# 내부적으로 결제 완료 점검, 후처리
class OrderImpAjaxView(View):
    def post(self, request, *args, **kwargs):
        # 로그인을 하지 않은 경우
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated": False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)

        merchant_id = request.POST.get('merchant_id')
        imp_id = request.POST.get('imp_id')
        amount = request.POST.get('amount')

        try:
            trans = OrderTransaction.objects.get(
                order=order,
                merchant_order_id=merchant_id,
                amount=amount
            )
        except:
            trans = None

        if trans is not None:
            trans.transaction_id = imp_id
            #trans.success = True
            # save 전 order_payment_validation 실행
            trans.save()
            order.paid = True
            order.save()

            data = {
                "works":True
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)


from .cart import Cart
# 모든 페이지에서 cart정보 알수있게 하기위해 사용
def cart(request):
    cart = Cart(request)
    return {'cart':cart}
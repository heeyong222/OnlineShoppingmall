from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

from shop.models import Product
from coupon.models import Coupon
# Create your models here.
class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # 결제 완료 여부
    paid = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name='order_coupon', null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])

    class Meta:
        ordering = ['-created']
    # 객체 자체를 출력했을때 필요한 기능
    def __str__(self):
        return f'Order {self.id}'

    def get_total_product(self):
        return sum(item.get_item_price() for item in self.items.all())

    def get_total_price(self):
        total_product = self.get_total_product()
        return total_product - self.discount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_products')
    price = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)
    # 제품 총 가격
    def get_item_price(self):
        return self.price * self.quantity

# *.objects = manager
# db 작업을 위한 manager
import hashlib
from .iamport import payments_prepare, find_transaction
class OrderTransactionManager(models.Manager):
    def create_new(self, order, amount, success=None, transaction_status=None):
        if not order:
            raise ValueError("주문 정보 오류")
        # 암호화하여 주문번호 생성
        order_hash = hashlib.sha1(str(order.id).encode('utf-8')).hexdigest()
        email_hash = str(order.email).split("@")[0]
        final_hash = hashlib.sha1((order_hash+email_hash).encode('utf-8')).hexdigest()[:10]
        merchant_order_id = str(final_hash)
        # iamport에 결제 정보 전달
        payments_prepare(merchant_order_id, amount)
        # 결제
        transaction = self.model(
            order=order,
            merchant_order_id=merchant_order_id,
            amount=amount
        )
        # 결제 테스트
        if success is not None:
            transaction.success = success
            transaction.transaction_status = transaction_status

        try:
            transaction.save()
        except Exception as e:
            print("transaction save error", e)

        return transaction.merchant_order_id

    def get_transaction(self, merchant_order_id):
        result = find_transaction(merchant_order_id)
        if result['status'] == 'paid':
            return result
        else:
            return None

# 결제 관련 정보
class OrderTransaction(models.Model):
    # order 정보가 없다면 결제정보도 없어져야 하기 때문에 CASCADE 사용
    # max_length는 결제대행사 별로 상이하기때문에 맞게 설정
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    merchant_order_id = models.CharField(max_length=20, null=True, blank=True)
    transaction_id = models.CharField(max_length=20, null=True, blank=True)
    amount = models.PositiveIntegerField(default=0)
    transaction_status = models.CharField(max_length=220, null=True, blank=True)
    type = models.CharField(max_length=120, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    #success = models.BooleanField(default=False)
    objects = OrderTransactionManager()

    def __str__(self):
        return str(self.order.id)

    class Meta:
        ordering = ['-created']

# 시그널 : 어떤일을 시작하기전 또는 후에 뭔가를 하고싶을때
def order_payment_validation(sender, instance, created, *args, **kwargs):
    if instance.transaction_id:
        import_transaction = OrderTransaction.objects.get_transaction(merchant_order_id=instance.merchant_order_id)
        merchant_order_id = import_transaction['merchant_order_id']
        imp_id = import_transaction['imp_id']
        amount = import_transaction['amount']

        local_transaction = OrderTransaction.objects.filter(merchant_order_id=merchant_order_id, transaction_id=imp_id, amount=amount).exists()

        if not import_transaction or not local_transaction:
            raise ValueError("비정상 거래입니다.")
# 모델에 어떤 일이 발생하였을때
# OrderTransaction에 save가 일어날때 반복적으로 처리
from django.db.models.signals import post_save
post_save.connect(order_payment_validation, sender=OrderTransaction)
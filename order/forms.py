from django import forms
from .models import Order
# form : 사용자들이 정보를 서버에 보낼때 정제된 모습으로 하기 위해 사용
# 해킹시도, 사용자가 잘못입력하는 등의 경우에 유효성 검사를 진행하여 cleandata로 만드는데 관여
# 특정 모델에 관한 form : ModelForm사용, 모델은 없는경우는 일반Form 사용
class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','email','address',
                  'postal_code','city']
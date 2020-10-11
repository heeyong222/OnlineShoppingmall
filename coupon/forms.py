from django import forms

class AddCouponForm(forms.Form):
    code = forms.CharField(label='쿠폰 입력')
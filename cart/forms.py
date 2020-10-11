from django import forms
# form의 역할
# 1. 클라이언트 화면에 입력 폼을 만드는 역할
# 2. 클라이언트가 입력한 데이터에 대한 전처리

class AddProductForm(forms.Form):
    quantity = forms.IntegerField()
    is_update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
import requests
from django.conf import settings

# apikey와 secretkey로 iamport에 로그인처리하는 기능
# api통신하려면 토큰이 필요한데 매번 통신할때마다 새로 받아옴
def get_token():
    access_data = {
        'imp_key':settings.IAMPORT_KEY,
        'imp_secret':settings.IAMPORT_SECRET
    }
    url = "https://api.iamport.kr/users/getToken"
    # url, key와 secret으로 데이터 받아옴
    req = requests.post(url, data=access_data)
    access_res = req.json()
    # 제대로 요청이 온 경우
    if access_res['code'] is 0:
        return access_res['response']['access_token']
    else:
        return None

# 어떤 orderid로 얼마만큼의 결제를 요청할지 iamport에 등록
def payments_prepare(order_id, amount, *args, **kwargs):
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant_uid':order_id,
            'amount':amount
        }
        url = "https://api.iamport.kr/payments/prepare"
        # 토큰 삽입
        headers = {
            'Authorization':access_token
        }
        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
    else:
        raise ValueError("토큰 오류")


# 결제 완료 후 iamport에 남은 기록으로 확인
def find_transaction(order_id, *args, **kwargs):
    access_token = get_token()
    if access_token:
        url = "https://api.iamport.kr/payments/find/"+order_id
        headers = {
            'Authorization':access_token
        }
        req = requests.post(url, headers=headers)
        res = req.json()
        if res['code'] == 0:
            context = {
                'imp_id':res['response']['imp_uid'],
                'merchant_order_id':res['response']['merchant_uid'],
                'amount':res['response']['amount'],
                'status':res['response']['status'],
                'type':res['response']['pay_method'],
                'receipt_url':res['response']['receipt_url']
            }
            return context
        else:
            return None
    else:
        raise ValueError("토큰 오류")
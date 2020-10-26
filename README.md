# HEEYONGSHOP 
Python Django Online ShoppingMall 
## Installation
    pip install django
    pip install pillow
    pip install boto3
    pip install django-allauth
    pip install django-storages
    pip install pymysql
## Category
* 신상품
* 세일중
* OUTER
* TOP
* PANTS
* SHOES
* ACC
  ### List of Product
  - Show products in the order updated
  - Show product's picture, model_name, price, saled_price, stock
## Cart
* Can see your cart counts at every page by using context processor
* Can change the quantity of products
* Show unit price and total price
* Can add Coupon
  ### Coupon
  - can add at admin page
  - Coupon_code
  - Expiration date
  - Coupon_price
  - Quantity
## Payment
* Show cart list
* need to input
 * First name
 * Last name
 * Email
 * Address
 * Postal Code
* Can pay kginisis by using iamport api
* If payment ended, can check order in admin page

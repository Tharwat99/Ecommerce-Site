from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import(
	HomeView, 
	product_detail, 
	OrderSummaryView,
	add_to_cart,
	remove_from_cart,
	remove_single_item_from_cart,
	CheckoutView,
	PaymentView,
	AddCouponView,
	RequsetRefundView,
	RemoveCouponView,
)

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name = 'home'),
    path('product/<slug>/', product_detail, name = 'product'),
    path('check-out/',CheckoutView.as_view(), name = 'check_out'),
    path('add-coupon/',AddCouponView.as_view(), name = 'add_coupon'),
    path('remove-coupon/',RemoveCouponView.as_view(), name = 'remove_coupon'),
    path('payment/<payment_option>/',PaymentView.as_view(), name = 'payment'),
    path('order-summary/', OrderSummaryView.as_view(), name = 'order_summary'),
    path('request-refund/', RequsetRefundView.as_view(), name = 'request_refund'),
    path('add-to-cart/<slug>/', add_to_cart, name = 'add_to_cart'),
    path('remove-from_cart/<slug>/', remove_from_cart, name = 'remove_from_cart'),
	path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name = 'remove_single_item_from_cart'),
]
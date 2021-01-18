from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address , UserProfile, Category, Tag
from django.contrib.auth.decorators import login_required

admin.site.login = login_required(admin.site.login)

class ItemAdmin(admin.ModelAdmin):
	list_display = ['id', 'title', 'price', 'discount_price','tag','category'] 
	list_display_links = ['id'] 
	list_filter   = ['title', 'price','tag','category']
	search_fields = ['title', 'price','tag','category']  
	

class OrderItemAdmin(admin.ModelAdmin):
	list_display = ['id','user', 'item', 'quantity','ordered'] 
	list_display_links = ['id'] 
	list_filter   = ['user', 'item__title'] 
	search_fields = ['user__username', 'item__title'] 


def make_refund_accepted(modeladmin, request, Queryset):
	Queryset.update(refund_requested = False, refund_granted = True)
make_refund_accepted.short_description =  'Update orders to refund granted'

class OrderAdmin(admin.ModelAdmin):
	list_display = ['id','user', 'shipping_address', 'billing_address','Payment','Coupon','ordered',
	'being_delivered', 'received', 'refund_requested', 'refund_granted'] 
	list_display_links = ['user', 'shipping_address', 'billing_address', 'Payment','Coupon'] 
	list_filter   = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted'] 
	#search_fields = ['user__username', 'ref_code'] 
	actions = [make_refund_accepted]

class AddressAdmin(admin.ModelAdmin):
	list_display =[ 
	'id',
	'user',
	'address_type',
	'street_address',
	'apartment_address',
	'country',
	'zip',
	'default_address'
	]
	list_filter = ['id', 'default_address', 'address_type','country']
	search_fields = ['user__username','address_type','default_address','street_address', 'apartment_address','zip']
class CategoryAdmin(admin.ModelAdmin):
	list_display =[ 
	'id',
	'title',
	'label',
	]
	list_filter = ['title', 'label']
	search_fields = ['title', 'label']
class PaymentAdmin(admin.ModelAdmin):
	list_display =[ 
	'user',
	'stripe_charge_id',
	'amount',
	'timestamp',
	]
	list_filter = ['stripe_charge_id', 'amount','user', 'timestamp']
	search_fields = ['user__username']
class CouponAdmin(admin.ModelAdmin):
	list_display = [
		'id',
		'code',
		'amount',
	]	
	list_filter = ['code', 'amount']
	search_fields = ['code', 'amount']
class RefundAdmin(admin.ModelAdmin):
	list_display = [
	'order','reason','accepted','email'
	]
	list_filter = ['order','reason','accepted','email']
	search_fields = ['order','reason','accepted','email']

class TagAdmin(admin.ModelAdmin):
	list_display = [
	'id', 'title','label'
	]
	list_filter = ['title','label']
	search_fields = ['title','label']

class UserPAdmin(admin.ModelAdmin):
	list_display = [
	'id', 'user','stripe_customer_id','on_click_purchasing'
	]
	list_filter = ['user','stripe_customer_id','on_click_purchasing']
	search_fields = ['user','stripe_customer_id','on_click_purchasing']
admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Refund, RefundAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(UserProfile, UserPAdmin)
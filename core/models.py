from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
# Create your models here.

CATEGORY_CHOICES = (
	('S' , _('Shirt')),
	('TS' , _('T-Shirt')),
	('SW', _('Sport Wear')),
	('OW', _('OutWear')),
	('PA', _('Pant')),
	('H', _('Hats')),
)
LABEL_CHOICES = (
	('P', 'primary'),
	('Se', 'secondary'),
	('Su', 'success'),
	('W', 'warning'),
	('Dan', 'danger'),
	('Dar', 'dark'),
	('L', 'light'),


)
ADDRESS_CHOICES = (
	('B' , 'Billing'),
	('S', 'Shipping')
)

class Tag(models.Model):
	title 	= models.CharField(max_length = 50, verbose_name=_('Title'))				
	label   = models.CharField(choices = LABEL_CHOICES, max_length = 3, null =  True, blank = True, verbose_name=_('Label'))
	class Meta:
		verbose_name = _('tags')
		verbose_name_plural = _('tags')
	def __str__(self):
		return self.title

class Category(models.Model):
	title   = models.CharField(max_length = 50 , verbose_name=_('Title'))
	label   = models.CharField(choices = LABEL_CHOICES, max_length = 3, null =  True, blank = True,  verbose_name=_('Label'))
	
	class Meta:
		verbose_name = _('categories')
		verbose_name_plural = _('categories')
	
	def __str__(self):
		return self.title
class Item(models.Model):
	title 	 		= models.CharField(max_length = 100, verbose_name=_('Title'))
	price 	 		= models.FloatField(verbose_name=_('Price'))
	discount_price  = models.FloatField(null =  True, blank = True, verbose_name=_('Discount Price'))
	category        = models.ForeignKey('Category', on_delete = models.CASCADE, null =  True, blank = True,  verbose_name=_('Category')) 
	tag          	= models.ForeignKey('Tag', on_delete = models.CASCADE, null =  True, blank = True, verbose_name=_('Tag'))
	slug     		= models.SlugField(verbose_name=_('Slug'))
	description 	= models.TextField(null =  True, blank = True, verbose_name=_('Description'))
	image			= models.ImageField(null =  True, blank = True, verbose_name=_('Image'))
	class Meta:
		verbose_name = _('items')
		verbose_name_plural = _('items')
	
	def __str__ (self):
		return self.title
	
	def get_absolute_url(self): 
		return reverse('core:product',kwargs = {
			'slug' : self.slug
			})	
	def add_to_cart(self):
		return reverse('core:add_to_cart',kwargs = {
			'slug' : self.slug
			})
	def remove_from_cart(self):
		return reverse('core:remove_from_cart',kwargs = {
		'slug' : self.slug
		})	

class OrderItem(models.Model):
	user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name=_('User'))
	ordered      = models.BooleanField(default = False, verbose_name = _('Ordered'))
	item         = models.ForeignKey(Item, on_delete = models.CASCADE	, verbose_name=_('Item')) 
	quantity     = models.IntegerField(default = 1, verbose_name=_('Quantity'))
	class Meta:
		verbose_name = _('order items')
		verbose_name_plural = _('order items')
	def __str__ (self):
		return self.item.title
	def get_total_price(self):
		return self.quantity * self.item.price
	def get_total_discount_price(self):
		return self.quantity * self.item.discount_price
	def get_amount_save(self):
		return self.quantity * (self.item.price - self.item.discount_price)	
	def get_final_price(self):
		if self.item.discount_price:
			return self.get_total_discount_price()
		return self.get_total_price()		

class Order(models.Model):
	user           		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name=_('user'))
	ref_code			= models.CharField(max_length = 20,  blank = True, null = True, verbose_name=_('refernce code'))
	items          		= models.ManyToManyField(OrderItem, verbose_name=_('items'))
	ordered        		= models.BooleanField(default = False, verbose_name=_('ordered'))
	being_delivered     = models.BooleanField(default = False, verbose_name=_('being delivered'))
	received       		= models.BooleanField(default = False, verbose_name=_('received'))
	refund_requested   	= models.BooleanField(default = False, verbose_name=_('refund requested'))
	refund_granted     	= models.BooleanField(default = False, verbose_name=_('refund granted'))
	start_date     		= models.DateTimeField(auto_now_add = True, verbose_name=_('start date'))
	ordered_date   		= models.DateTimeField(verbose_name=_('ordered date')) 
	billing_address     = models.ForeignKey('Address', related_name = 'billing_adddress', on_delete = models.SET_NULL, blank = True, null = True, verbose_name=_('billing address'))
	shipping_address    = models.ForeignKey('Address', related_name = 'shipping_adddress', on_delete = models.SET_NULL, blank = True, null = True, verbose_name=_('shipping address'))
	Payment		   		= models.ForeignKey('Payment', on_delete = models.SET_NULL, blank = True, null = True, verbose_name=_('Payment'))
	Coupon		   		= models.ForeignKey('Coupon', on_delete = models.SET_NULL, blank = True, null = True, verbose_name=_('Coupon Code'))
	class Meta:
		verbose_name = _('order')
		verbose_name_plural = _('order')

	def __str__ (self):
		return self.user.username
	def total_order(self):
		total = 0
		for order_item in self.items.all()	:
			total += order_item.get_final_price()
		if self.Coupon :
			total-= self.Coupon.amount	
		return total

class Address(models.Model):
	user              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name=_('user'))
	street_address    = models.CharField(max_length = 100, verbose_name=_('street address'))
	apartment_address = models.CharField(max_length = 100, verbose_name=_('apartment address'))
	country           = CountryField(multiple = False, verbose_name=_('country'))
	zip 			  = models.CharField(max_length = 100, verbose_name=_('zip'))
	address_type	  = models.CharField(max_length = 1, choices = ADDRESS_CHOICES, verbose_name=_('address type'))
	default_address   = models.BooleanField(default = False, verbose_name=_('default address'))       	
	class Meta:
		verbose_name = _('addresses')
		verbose_name_plural = _('addresses')

	def __str__(self):
		return self.user.username	

class Payment(models.Model):
	stripe_charge_id = models.CharField(max_length = 100, verbose_name=_('stripe charge id'))
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, blank = True, null = True, verbose_name=_('user'))
	amount = models.FloatField(verbose_name =_('amount'))
	timestamp = models.DateTimeField(auto_now_add = True, verbose_name=_('Time'))
	class Meta:
		verbose_name = _('Payments')
		verbose_name_plural = _('Payments')

class Coupon(models.Model):
	code   = models.CharField(max_length = 20, verbose_name=_('code'))
	amount = models.FloatField(verbose_name=_('amount')) 
	class Meta:
		verbose_name = _('coupons')
		verbose_name_plural = _('coupons')
	def __str__(self):
		return self.code		

class Refund(models.Model):
	order    = models.ForeignKey(Order, on_delete = models.CASCADE, verbose_name=_('order'))
	reason   = models.TextField(verbose_name=_('reason'))
	accepted = models.BooleanField(default =False, verbose_name=_('accepted'))
	email    = models.EmailField(verbose_name=_('email'))
	class Meta:
		verbose_name = _('Refunds')
		verbose_name_plural = _('Refunds')
	def __str__(self):
		return f"{self.pk}"	 		

class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name=_('user'))
	stripe_customer_id  = models.CharField(max_length = 100, blank = True, null = True, verbose_name=_('stripe customer id'))
	on_click_purchasing = models.BooleanField(default = False, verbose_name=_('on click on_click_purchasing'))
	class Meta:
		verbose_name = _('Users Profile')
		verbose_name_plural = _('Users Profile')		
	def  __str__(self):
		return self.user.username	

def user_profile_receiver(sender, instance, created, *args, **kwargs):
	if created:
		user_profile = UserProfile.objects.create(user = instance)

post_save.connect(user_profile_receiver, sender = settings.AUTH_USER_MODEL)	
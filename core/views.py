from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import  ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View 
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Category
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CheckOutForm, CouponForm, RequsetRefundForm
import stripe
import random
import string
stripe.api_key = settings.STRIP_SECRET_KEY

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k = 20))

class HomeView (View):
	def get(self, *args, **kwargs):
		products   = Item.objects.all()	
		categories = Category.objects.all()
		query      =  self.request.GET.get('query')
		if query:		
			products = Item.objects.filter(
				Q (category__title__icontains = query)|
				Q (tag__title__icontains = query)|
				Q (title__icontains = query)|
				Q (price__icontains = query)
			).distinct()		 
		paginator = Paginator(products, 20)
		page = self.request.GET.get('page')
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)	
		context ={
			'products'    : products,
			'categories'  : categories,
			'query'       : query, 	
		}
		return render(self.request,'index.html',context)

def product_detail(request, slug = None):
	product = Item.objects.get(slug = slug)
	#%%%%%% Need To update don't forget may any product without any tag R55%%%%%
	additional_products = Item.objects.filter(
				Q (category__title = product.category.title)|
				Q (tag__title = product.tag.title)
			).distinct()
	context ={
		'product'    : product,
		'additional_products'  : additional_products}
	return render(request,'product.html',context)

def is_valid_form(values):
	for value in values:
		if value == '':
			return False
	return True		


class CheckoutView(View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user = self.request.user, ordered = False)	
			form = CheckOutForm()
			context = {
				'form' : form,
				'couponform': CouponForm(),
				'order':order,
				'DISPLAY_COUPON_FORM':True,
			} 
			# update default shipping address if new one exists
			shipping_address_qs = Address.objects.filter(
				user = self.request.user,
				address_type = 'S',
				default_address = True,
			)
			if shipping_address_qs.exists():
				context.update({'default_shipping_address':shipping_address_qs.first()})
			# update default billing address if new one exists	
			billing_address_qs = Address.objects.filter(
				user = self.request.user,
				address_type = 'B',
				default_address = True,
			)
			if billing_address_qs.exists():
				context.update({'default_billing_address':billing_address_qs.first()})
			return render(self.request, 'checkout.html', context)
		
		except ObjectDoesNotExist:
			messages.info(self.request, 'You do not have and active order cart')	
			return redirect('/')
		
	def post(self, *args, **kwargs)	:
		try:
			order = Order.objects.get(user = self.request.user , ordered = False)
			form = CheckOutForm(self.request.POST or None)
			if form.is_valid():
				# Shipping address assign data to order
				use_default_shipping = form.cleaned_data.get('use_default_shipping')
				if use_default_shipping:
					shipping_address_qs = Address.objects.filter(
					user = self.request.user,
					address_type = 'S',
					default_address = True,
					)
					if shipping_address_qs.exists():
						shipping_address = shipping_address_qs.first()
						order.shipping_address = shipping_address
						order.save()	
					else:
						messages.warning(self.request, 'No default shipping address avaliable please fill fields')
						return redirect('core:check_out')
				else:
					shipping_address1  = form.cleaned_data.get('shipping_address1')
					shipping_address2 = form.cleaned_data.get('shipping_address2')
					shipping_country  = form.cleaned_data.get('shipping_country')
					shipping_zip      = form.cleaned_data.get('shipping_zip')

					if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
						shipping_address = Address(
						user = self.request.user,
						street_address = shipping_address1,
						apartment_address = shipping_address2,
						country = shipping_country,
						zip = shipping_zip,
						address_type = 'S'
						)
						shipping_address.save()	
						order.shipping_address = shipping_address
						order.save()
						set_default_shipping = form.cleaned_data.get('set_default_shipping')
						if set_default_shipping:
							shipping_address_qs = Address.objects.filter(
							user = self.request.user,
							address_type = 'S',
							default_address = True,
							)
							if shipping_address_qs.exists():
								updated_default_shipping_address = Address(
									user = shipping_address_qs.first().user,
									street_address = shipping_address_qs.first().street_address,
									apartment_address = shipping_address_qs.first().apartment_address,
									country = shipping_address_qs.first().country,
									zip = shipping_address_qs.first().zip,
									address_type = 'S',
									default_address = False
								)
								updated_default_shipping_address.save()
								shipping_address_qs.first().delete()
							shipping_address.default_address = True
							shipping_address.save()		
					else:
						messages.warning(self.request, 'Please Fill Shipping Address Fields')
						return redirect('core:check_out')
				# Billing address assign data to order
				use_default_billing = form.cleaned_data.get('use_default_billing')
				same_billing_address = form.cleaned_data.get('same_billing_address')
				
				if same_billing_address :
					billing_address = shipping_address
					billing_address.pk = None
					billing_address.save()
					billing_address.address_type = 'B'
					billing_address.save()
					order.billing_address = billing_address
					order.save()
				elif use_default_billing:
					billing_address_qs = Address.objects.filter(
					user = self.request.user,
					address_type = 'B',
					default_address = True,
					)
					if billing_address_qs.exists():
						billing_address = billing_address_qs.first()
						order.billing_address = billing_address
						order.save()
					else:
						messages.warning(self.request, 'No default billing address avaliable please fill in fields')
						return redirect('core:check_out')
				else:
					billing_address1  = form.cleaned_data.get('billing_address1')
					billing_address2 = form.cleaned_data.get('billing_address2')
					billing_country  = form.cleaned_data.get('billing_country')
					billing_zip      = form.cleaned_data.get('billing_zip')

					if is_valid_form([billing_address1, billing_country, billing_zip]):
						billing_address = Address(
						user = self.request.user,
						street_address = billing_address1,
						apartment_address = billing_address2,
						country = billing_country,
						zip = billing_zip,
						address_type = 'B'
						)
						billing_address.save()	
						order.billing_address = billing_address
						order.save()
						set_default_billing = form.cleaned_data.get('set_default_billing')
						if set_default_billing:
							billing_address_qs = Address.objects.filter(
							user = self.request.user,
							address_type = 'B',
							default_address = True,
							)
							if billing_address_qs.exists():
								updated_default_billing_address = Address(
									user = billing_address_qs.first().user,
									street_address = billing_address_qs.first().street_address,
									apartment_address = billing_address_qs.first().apartment_address,
									country = billing_address_qs.first().country,
									zip = billing_address_qs.first().zip,
									address_type = 'B',
									default_address = False
								)
								updated_default_billing_address.save()
								billing_address_qs.first().delete()
							billing_address.default_address = True
							billing_address.save()
					else:
						messages.warning(self.request, 'Please Fill Billing Address Fields')
						return redirect('core:check_out')	
				# payment methods 
				payment_option  = form.cleaned_data.get('payment_option')
				if payment_option == 'S':

					return redirect('core:payment',payment_option = 'stripe')
				elif payment_option == 'P':
					return redirect('core:payment',payment_option = 'pypal')
				else:			
					messages.warning(self.request, 'Invalid payment option selected')
					return redirect('core:check_out')
		except ObjectDoesNotExist:
			messages.error(self.request, 'you do not have an active order')
			return redirect('core:order_summary')

class PaymentView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order  = Order.objects.get(user = self.request.user, ordered = False)	
			if order.billing_address:	
				context = {
					'order' : order,
					'DISPLAY_COUPON_FORM':False,
				}
				try:
					user_profile  = self.request.user.userprofile
				except ObjectDoesNotExist:
					 	user_profile = UserProfile.objects.create(user = self.request.user)
				if user_profile.on_click_purchasing:
					cards = stripe.Customer.list_sources(
						user_profile.stripe_customer_id,
						limit = 3,
						object = 'card'
					)
					card_list = cards['data']
					if len(card_list) > 0:
						context.update({'card' : card_list[0]})
				return render(self.request, 'payment.html',context)	
			else:
				messages.warning(self.request, 'you do not have a billing address')
				return redirect('core:check_out')	
		except ObjectDoesNotExist:
			messages.warning(self.request, 'you do not have an active order xx')
			return redirect('/')	
	def post(self, *args, **kwargs):
		order  = Order.objects.get(user = self.request.user, ordered = False)
		#form   = form(self.request.POST or None)
		user_profile = UserProfile.objects.get(user = self.request.user)
		amount       = int(order.total_order() * 100) 
		token        = self.request.POST.get('stripeToken')
		save         = self.request.POST.get('save_card_info')
		use_default  = self.request.POST.get('use_default')
		if save:
			if not user_profile.stripe_customer_id:
				customer = stripe.Customer.create(
					email    = self.request.user.email,
					source   = token	
				)
				user_profile.stripe_customer_id  = customer['id']
				user_profile.on_click_purchasing = True
				user_profile.save()	
			else:
				stripe.Customer.create_source(
					user_profile.stripe_customer_id,
					source = token,
				)
			try:
				charge = stripe.Charge.create(
					amount = amount,
					currency = 'usd',
					source = token
				)
			except stripe.error.CardError as e:
				body = e.json_body
				err = body.get('error', {})
				messages.warning(self.request, f"{err.get('message')}")
				return redirect('/')
			except stripe.error.InvalidRequestError as e:
				messages.warning(self.request, "Invalid Parameters Error !")
				return redirect('/')
			except stripe.error.RateLimitError as e :
				messages.warning(self.request, "Rate Limit Error !")
				return redirect('/')
			except stripe.error.AuthenticationError as e :
				messages.warning(self.request, "No Authenticated Error !")
				return redirect('/')
			except stripe.error.APIConnectionError as e :
				messages.warning(self.request, "Network Connection Error !")
				return redirect('/')
			except stripe.error.StripeError as e:
				messages.warning(self.request, "Something get wrong, You were not charged, please try again !")
				return redirect('/')
			except Exception as e :	
				messages.warning(self.request, "A serious error occurred !!")	
				return redirect('/')	
		elif use_default :
			try:
				charge = stripe.Charge.create(
					amount = amount,
					currency = 'usd',
					source = token,
					customer =  user_profile.stripe_customer_id
				)
			except stripe.error.CardError as e:
				body = e.json_body
				err = body.get('error', {})
				messages.warning(self.request, f"{err.get('message')}")
				return redirect('/')
			except stripe.error.InvalidRequestError as e:
				messages.warning(self.request, "Invalid Parameters Error !")
				return redirect('/')
			except stripe.error.RateLimitError as e :
				messages.warning(self.request, "Rate Limit Error !")
				return redirect('/')
			except stripe.error.AuthenticationError as e :
				messages.warning(self.request, "No Authenticated Error !")
				return redirect('/')
			except stripe.error.APIConnectionError as e :
				messages.warning(self.request, "Network Connection Error !")
				return redirect('/')
			except stripe.error.StripeError as e:
				messages.warning(self.request, "Something get wrong, You were not charged, please try again !")
				return redirect('/')
			except Exception as e :	
				messages.warning(self.request, "A serious error occurred !!")	
				return redirect('/')			
		else:
			try:
				charge = stripe.Charge.create(
					amount = amount,
					currency = 'usd',
					source = token
				)
			except stripe.error.CardError as e:
				body = e.json_body
				err = body.get('error', {})
				messages.warning(self.request, f"{err.get('message')}")
				return redirect('/')
			except stripe.error.InvalidRequestError as e:
				messages.warning(self.request, "Invalid Parameters Error !")
				return redirect('/')
			except stripe.error.RateLimitError as e :
				messages.warning(self.request, "Rate Limit Error !")
				return redirect('/')
			except stripe.error.AuthenticationError as e :
				messages.warning(self.request, "No Authenticated Error !")
				return redirect('/')
			except stripe.error.APIConnectionError as e :
				messages.warning(self.request, "Network Connection Error !")
				return redirect('/')
			except stripe.error.StripeError as e:
				messages.warning(self.request, "Something get wrong, You were not charged, please try again !")
				return redirect('/')
			except Exception as e :	
				messages.warning(self.request, "A serious error occurred !!")	
				return redirect('/')
		#create payment
		payment = Payment()
		payment.stripe_charge_id = charge['id']
		payment.user = self.request.user
		payment.amount = order.total_order()
		payment.save() 	

		order_items = order.items.all()
		order_items.update(ordered= True)
		for order_item in order_items:
			order_item.save()
		order.ordered = True
		#assign payment to orders	
		order.Payment = payment
		order.ref_code = create_ref_code()
		order.save()
		messages.success(self.request, 'Your Order Was Successfully ')
		return redirect('/')
		
class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user = self.request.user , ordered = False)
			context = {
				'object' : order,
			}
			return render(self.request, 'order_summary.html',context)
		except ObjectDoesNotExist:
			messages.warning(self.request, 'you do not have an active order')
			print('you do not have an active order')	
			return redirect('/')
		
@login_required
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug =slug) 
	order_item, created = OrderItem.objects.get_or_create(
		user = request.user,
		item = item,
		ordered  = False	
		)
	order_qs = Order.objects.filter(user = request.user, ordered = False)
	if order_qs.exists():
		order = order_qs.first()
		#then check if order item in the orders
		if order.items.filter(item__slug = item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request, 'This item quantity updated ')	
			return redirect("core:order_summary")		
		else :
			order.items.add(order_item)
			messages.info(request, 'This item added to your cart')	
			print('this item added to your cart')	 		
			return redirect("core:order_summary")		
	else	:
		ordered_date = timezone.now() 
		order = Order.objects.create(user = request.user, ordered_date = ordered_date)
		order.items.add(order_item)
		messages.info(request, 'This item added to your cart')
		return redirect("core:order_summary")

@login_required
def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug = slug) 	
	order_qs = Order.objects.filter(user = request.user, ordered = False)
	if order_qs.exists():
		order = order_qs.first()
		if order.items.filter(item__slug = item.slug).exists():
			order_item = OrderItem.objects.filter(
				item  = item,
				user  = request.user,
				ordered = False,
			).first()
			order.items.remove(order_item)
			order_item.delete()
			messages.info(request, 'This item removed from your cart')
			print('This item removed from your cart')
			return redirect("core:order_summary")
		else:
			messages.info(request, 'This item was not in  your cart')
			print('This item was not in  your cart')
			return redirect("core:product",slug = slug)				
	else:
		messages.info(request, 'You do not have and active order cart')
		print('You do not have and active order')
		return redirect("core:product",slug = slug)

@login_required
def remove_single_item_from_cart(request, slug):
	item = get_object_or_404(Item, slug = slug) 	
	order_qs = Order.objects.filter(user = request.user, ordered = False)
	if order_qs.exists():
		order = order_qs.first()
		if order.items.filter(item__slug = item.slug).exists():
			order_item = OrderItem.objects.filter(
				item  = item,
				user  = request.user,
				ordered = False,
			).first()
			if order_item.quantity > 1: 
				order_item.quantity -= 1
				order_item.save()
			else :
				order.items.remove(order_item)
				order_item.delete()
			messages.info(request, 'This item quantity was updated')
			print('This item quantity was updated')
			return redirect("core:order_summary")
		else:
			messages.info(request, 'This item was not in  your cart')
			print('This item was not in  your cart')
			return redirect("core:product",slug = slug)				
	else:
		messages.info(request, 'You do not have and active order cart')
		print('You do not have and active order')
		return redirect("core:product",slug = slug)
def get_coupon(request, code):
	try :
		coupon = Coupon.objects.get(code = code)
		return coupon
	except ObjectDoesNotExist:
		messages.info(request, 'This coupon does not exists')	
		return redirect('core:check_out')
class RemoveCouponView(View):
	def post(self, *args, **kwargs):
		form = CouponForm(self.request.POST or None)
		if form.is_valid():	
			try:
				code = form.cleaned_data.get('code')
				coupon = get_coupon(self.request, code)
				print(code)
				order = Order.objects.get(user = self.request.user, ordered = False)	
				if order.Coupon == coupon:	
					order.Coupon = None
					order.save()
					messages.info(request, 'This coupon removed Successfully')	
					return redirect('core:check_out')
				else:
					messages.info(request, 'This coupon does not exists')	
					return redirect('core:check_out')
			except ObjectDoesNotExist:
				messages.info(request, 'This coupon does not exists')	
				return redirect('core:check_out')
								
class AddCouponView(View):
	def post(self, *args, **kwargs):
		form = CouponForm(self.request.POST or None)
		if form.is_valid():	
			try:
				code = form.cleaned_data.get('code')
				order = Order.objects.get(user = self.request.user, ordered = False)	
				order.Coupon = get_coupon(self.request, code)
				order.save()
				messages.success(self.request, 'Success Added Coupon')	
				return redirect('core:check_out')
			except ObjectDoesNotExist:
				messages.info(self.request, 'You do not have and active order cart')	
				return redirect('core:check_out')
						
class RequsetRefundView(View):
	def get(self, *args, **kwargs):
		form = RequsetRefundForm()
		context = {
			'form' : form,
		}
		return render(self.request, 'request_refund.html',context)
	def post(self, *args, **kwargs):
		form = RequsetRefundForm(self.request.POST)
		if form.is_valid():
			ref_code = form.cleaned_data.get('ref_code')
			message  = form.cleaned_data.get('message')
			email  	 = form.cleaned_data.get('email')
			try :
				order = Order.objects.get(ref_code = ref_code) 
				order.refund_requested = True
				order.save()
				refund = Refund()
				refund.order = order
				refund.reason = message
				refund.email = email
				refund.save()
				messages.info(self.request, "Your request was received")
				return redirect('core:request_refund')	 	
			except ObjectDoesNotExist:
				messages.info(self.request, "This order does not exists")
				return redirect('core:request_refund')	

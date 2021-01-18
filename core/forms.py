from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYEMENT_CHOICES = (
	('S','Stripe'),
	('P','PayPal')
)
class CheckOutForm(forms.Form):
	# for shipping address
	shipping_address1    = forms.CharField(required = False)
	shipping_address2   = forms.CharField(required = False) 
	shipping_country    = CountryField(blank_label = '(select country)').formfield(
		required = False,widget = CountrySelectWidget(
		attrs = {
		'class' : 'custom-select d-block w-100 form-control',
		}
		)
	)
	shipping_zip       	 = forms.CharField(required = False)
	same_billing_address = forms.BooleanField(required = False)
	set_default_shipping = forms.BooleanField(required = False)
	use_default_shipping = forms.BooleanField(required = False)
	
	# for billing address
	billing_address1    = forms.CharField(required = False)
	billing_address2   = forms.CharField(required = False) 
	billing_country    = CountryField(blank_label = '(select country)').formfield(
		required = False, widget = CountrySelectWidget(
		attrs = {
		'class' : 'custom-select d-block w-100',
		}
		)
	)
	billing_zip       	 = forms.CharField(required = False	, localize=True)
	set_default_billing = forms.BooleanField(required = False)
	use_default_billing = forms.BooleanField(required = False)
	
	# for payment option
	payment_option       = forms.ChoiceField(widget = forms.RadioSelect, choices = PAYEMENT_CHOICES)
class CouponForm(forms.Form):
	code = forms.CharField(widget = forms.TextInput(attrs = {
		'class' : 'form-control',
		'placeholder' : 'Coupon code',
		'aria-label' : "Recipient's username",
		'aria-describedby': "basic-addon2",
	}))

class RequsetRefundForm(forms.Form):
	ref_code = forms.CharField()
	message  = forms.CharField(widget = forms.Textarea(attrs={
			'rows': 4
		}))
	email 	 = forms.EmailField()

	
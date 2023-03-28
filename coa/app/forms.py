from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth import forms as auth_forms
from django.forms import ModelForm
from django.contrib.auth.password_validation import validate_password
from django.forms.models import inlineformset_factory

#login form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder': 'Email Address'}),label='Email Address')
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder':'Password'}))
    
    def __init__(self, *args, **kwargs):
            super(LoginForm, self).__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'

    def clean(self, *args, **kwargs):

         username = self.cleaned_data.get("username")
         password = self.cleaned_data.get("password")

         if username and password:
            info = User.objects.filter(username=username,groups__name='Client').first()

            print("infor" , info)
            if not info:
               raise ValidationError("This Username does not exists")
            user = authenticate(username=username, password=password)
            if not user:
                if info.is_active: 
                    raise ValidationError("Invalid password")
                else:
                    raise ValidationError("This account is inactive.")
            return True


#item form
class ItemForm(ModelForm):
   
    class Meta:
        model = Item
        fields = ['store','category','subcategory',"supplier","image",'sku','name','price','moq','uom']
    
    def __init__(self, *args, **kwargs):
            self.store = kwargs.pop('store', None)
            super(ItemForm, self).__init__(*args, **kwargs)
            self.fields['store'].initial    = self.store
            self.fields['store'].widget     = forms.HiddenInput()
            self.fields['sku'].label        = 'SKU ID'
            self.fields['name'].label       = 'SKU Name'
            self.fields['price'].label      = 'Unit Price'
            self.fields['moq'].required     = True

            self.fields['uom'].label      = 'Unit of Measurement'
            self.fields['uom'].required   = True

            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'
    
    def clean_sku(self):
        sku = self.cleaned_data['sku']
        if self.instance.id and self.instance.id is not None:
            r = Item.objects.filter(sku__iexact=sku,store=self.store).exclude(id = self.instance.id)
        else:
            r = Item.objects.filter(sku__iexact=sku,store=self.store)
        if r.count():
            raise ValidationError('This SKU ID already exists.')
        return sku

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance.id and self.instance.id is not None:
            r = Item.objects.filter(name__iexact=name,store=self.store).exclude(id = self.instance.id)
        else:
            r = Item.objects.filter(name__iexact=name,store=self.store)
        if r.count():
            raise ValidationError('This SKU Name already exists.')
        return name

    def clean_price(self):
        price = self.cleaned_data.get('price', None)
        if price <=0 :
            raise ValidationError('UNIT PRICE should be greater than zero.')
        return price
    
    def clean_moq(self):
        moq = self.cleaned_data.get('moq', None)
        if moq <= 0 :
            raise ValidationError('MOQ should be greater than zero.')
        return moq


#Sales Data form
class SalesForm(ModelForm):
   
    class Meta:
        model = Sales
        fields = ['item','quantity','updatedOn']
    
    def __init__(self, *args, **kwargs):
            store = kwargs.pop('store', None)
            super(SalesForm, self).__init__(*args, **kwargs)
            self.fields['item'].queryset    =  Item.objects.filter(store=store).order_by('name')
            self.fields['updatedOn'].label   = 'updated On'
            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity', None)
        if quantity <= 0:
            raise ValidationError('Quantity should be greater than zero.')
        return quantity

#store information form
class StoreForm(ModelForm):
    
    class Meta:
        model = Store
        fields = ['user','name','address','city','state','zipcode','phone']

    def __init__(self, *args, **kwargs):
            user = kwargs.pop('user', None)
            super(StoreForm, self).__init__(*args, **kwargs)
            self.fields['user'].initial  = user
            self.fields['user'].widget   = forms.HiddenInput()

            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'

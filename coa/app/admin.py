from django.contrib import admin
from django.contrib.auth.admin import   UserAdmin as DjangoAdminUser
from django.utils.translation import  ugettext_lazy as _ 
from django import forms
from django.contrib.auth.models import User
from app.models import *
from django.utils.html import format_html

class CategoryForm(forms.ModelForm):
    
    class Meta:
        model = Category
        fields = ["name","publish"]
    
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

class CategoryAdmin(admin.ModelAdmin):

    form = CategoryForm
    list_display = ('name', 'publish')
    list_filter =('publish',)
    search_fields = ('name',)


class SubcategoryForm(forms.ModelForm):
    
    class Meta:
        model = Subcategory
        fields = ["name","category","publish"]
    
    def __init__(self, *args, **kwargs):
        super(SubcategoryForm, self).__init__(*args, **kwargs)

class SubcategoryAdmin(admin.ModelAdmin):

    form = SubcategoryForm
    list_display = ('name', 'category', 'publish')
    list_filter =('category', 'publish',)
    search_fields = ('name',)


class StoreForm(forms.ModelForm):
    
    class Meta:
        model = Store
        fields = ["user","name","address","city","state","zipcode","phone","publish"]
    
    def __init__(self, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)

class StoreAdmin(admin.ModelAdmin):

    form = StoreForm
    list_display = ("user","name","address","city","state","zipcode","phone","publish")
    list_filter =("user",'publish',)
    search_fields = ('name',)

class SupplierForm(forms.ModelForm):
    
    class Meta:
        model = Supplier
        fields = ["name","address","city","state","zipcode","email","phone","moq"]
    
    def __init__(self, *args, **kwargs):
        super(SupplierForm, self).__init__(*args, **kwargs)

class SupplierAdmin(admin.ModelAdmin):

    form = SupplierForm
    list_display = ("name","address","city","state","zipcode","email","phone","moq")
    search_fields = ('name',)


class ItemForm(forms.ModelForm):
    
    class Meta:
        model = Item
        fields = ["store","category","subcategory","supplier","image","sku","name","price","moq","uom","publish"]
    
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

class ItemAdmin(admin.ModelAdmin):

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.image.url))
        else:
            return format_html('<img src="{}" width="50" height="50"/>'.format('/static/no-image.jpg'))

    image_tag.short_description = 'Image'

    form = ItemForm
    list_display = ("image_tag","sku","name","price","moq","uom","store","category","subcategory","supplier")
    list_filter =("store","category","subcategory",'supplier','uom',)
    search_fields = ('name','sku',)


class SalesForm(forms.ModelForm):
    
    class Meta:
        model = Sales
        fields = ["item","quantity","updatedOn"]
    
    def __init__(self, *args, **kwargs):
        super(SalesForm, self).__init__(*args, **kwargs)

class SalesAdmin(admin.ModelAdmin):

    
    form = SalesForm
    list_display = ("item","quantity","revenue","updatedOn")
    list_filter =("item",'updatedOn',)

class StockForm(forms.ModelForm):
    
    class Meta:
        model = Stock
        fields = ["item","quantity","updatedOn"]
    
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)

class StockAdmin(admin.ModelAdmin):

    form = StockForm
    list_display = ("item","quantity","updatedOn")
    list_filter =("item",'updatedOn',)

class WeeklyItemsAvgForm(forms.ModelForm):
    
    class Meta:
        model = WeeklyItemsAvg
        fields = ["item","avg","ratio","mon","tue","wed","thu","fri","sat","sun"]
    
    def __init__(self, *args, **kwargs):
        super(WeeklyItemsAvgForm, self).__init__(*args, **kwargs)
        
class WeeklyItemsAvgInline(admin.TabularInline):
    model           = WeeklyItemsAvg
    extra           = 0
    form            = WeeklyItemsAvgForm

class WeeklySalesAdmin(admin.ModelAdmin):

    inlines = (WeeklyItemsAvgInline,)
    list_display = ('store', 'category','subcategory','tot','mon','tue','wed','thu','fri','sat','sun')
    list_filter =('store','category','subcategory')
    

class OrederItemForm(forms.ModelForm):
    
    class Meta:
        model = OrederItem
        fields = ["item","total_quantity","on_hand_quanty","order_quantity","moq"]
    
    def __init__(self, *args, **kwargs):
        super(OrederItemForm, self).__init__(*args, **kwargs)
        
class OrederItemInline(admin.TabularInline):
    model           = OrederItem
    extra           = 0
    form            = OrederItemForm

class OrderAdmin(admin.ModelAdmin):

    inlines = (OrederItemInline,)
    list_display = ('store', 'category','subcategory','is_placed','activate_day','order_type','createdAt')
    list_filter =('store','category','subcategory','order_type','is_placed')

# Register your models here.
admin.site.register(Category,CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(WeeklySales, WeeklySalesAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Supplier,SupplierAdmin)
admin.site.register(Salescharts)


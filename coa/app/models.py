from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
import uuid
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField

#Category Model
class Category(models.Model):
    token       = models.UUIDField(default= uuid.uuid4)
    name        = models.CharField(max_length=255, unique=True)
    publish     = models.BooleanField(default = True)
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt   = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

#Sub Category Model
class Subcategory(models.Model):
    token       = models.UUIDField(default= uuid.uuid4)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    name        = models.CharField(max_length=255)
    publish     = models.BooleanField(default = True)
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt   = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sub Category'
        verbose_name_plural = 'Sub Categories'

#Family Model
class Family(models.Model):
    token       = models.UUIDField(default= uuid.uuid4)
    name        = models.CharField(max_length=255, unique=True)
    publish     = models.BooleanField(default = True)
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt   = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Family'
        verbose_name_plural = 'Families'

#Store Model
class Store(models.Model):
    token           = models.UUIDField(default= uuid.uuid4)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    name            = models.CharField(max_length=255)
    address         = models.CharField(max_length=255)
    city            = models.CharField(max_length=255)
    state           = models.CharField(max_length=255)
    zipcode         = models.CharField(max_length=255)
    phone           = models.CharField(max_length=255,blank = True, null=True)
    publish         = models.BooleanField(default = True)
    createdAt       = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt       = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

#Supplier Model
class Supplier(models.Model):
    token           = models.UUIDField(default= uuid.uuid4)
    name            = models.CharField(max_length=255)
    address         = models.CharField(max_length=255)
    city            = models.CharField(max_length=255)
    state           = models.CharField(max_length=255)
    zipcode         = models.CharField(max_length=255)
    email           = models.EmailField(max_length=255)
    phone           = models.CharField(max_length=255,blank = True, null=True)
    moq             = models.FloatField(blank = True, null=True)
    publish         = models.BooleanField(default = True)
    createdAt       = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt       = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

#Item Model
class Item(models.Model):
    token       = models.UUIDField(default= uuid.uuid4)
    store       = models.ForeignKey(Store, on_delete=models.CASCADE)
    image       = models.ImageField(null=True, blank=True, upload_to="items/")
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    supplier    = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank = True, null=True)
    name        = models.CharField(max_length=255)
    sku         = models.CharField(max_length=255)
    price       = models.FloatField()
    moq         = models.IntegerField(blank = True, null=True, default=1)
    uom         = models.CharField(max_length=255, choices=(('mm','Millimeter'),('cm','Centimeters'),('m','Meter'),('mg','Milligram'),('g','Gram'),('kg','Kilograms'),('mel','Milliliter'),('l','Liter'),('q','Quantity')), blank = True, null=True)
    publish     = models.BooleanField(default = True)
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt   = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

#Sales Data Model
class Sales(models.Model):
    item        = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity    = models.IntegerField()
    revenue     = models.FloatField(blank = True, null=True)
    updatedOn   = models.DateField()
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.item.name

    class Meta:
        verbose_name = 'Sales Data'
        verbose_name_plural = 'Sales Datas'

#Stock Data Model
class Stock(models.Model):
    item        = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity    = models.IntegerField()
    updatedOn   = models.DateField()
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return self.item.name

    class Meta:
        verbose_name = 'Stock Data'
        verbose_name_plural = 'Stock Datas'


#Store charts
class Salescharts(models.Model):
    token       = models.UUIDField(default= uuid.uuid4)
    store       = models.ForeignKey(Store, on_delete=models.CASCADE)
    chart1      = JSONField(null=True, blank = True)
    chart2      = JSONField(null=True, blank = True)
    chart3      = JSONField(null=True, blank = True)
    chart4      = JSONField(null=True, blank = True)
    chart5      = JSONField(null=True, blank = True)
    chart6      = JSONField(null=True, blank = True)
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt   = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return str(self.store)

    class Meta:
        verbose_name = 'Sales Chart'
        verbose_name_plural = 'Sales Charts'

#Weekly Sales Data Model
class WeeklySales(models.Model):
    token       = models.UUIDField(default= uuid.uuid4)
    store       = models.ForeignKey(Store, on_delete=models.CASCADE)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    mon         = models.FloatField()
    tue         = models.FloatField()
    wed         = models.FloatField()
    thu         = models.FloatField()
    fri         = models.FloatField()
    sat         = models.FloatField()
    sun         = models.FloatField()
    tot         = models.FloatField()
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return str(self.store)+' - '+str(self.category)+' - '+str(self.subcategory)+' - '+str(self.createdAt)

    class Meta:
        verbose_name = 'Weekly Sales Data'
        verbose_name_plural = 'Weekly Sales Data'

#Weekly Item Avg Data
class WeeklyItemsAvg(models.Model):
    salesweek   = models.ForeignKey(WeeklySales, on_delete=models.CASCADE)
    item        = models.ForeignKey(Item, on_delete=models.CASCADE)
    avg         = models.FloatField()
    ratio       = models.FloatField()
    mon         = models.FloatField()
    tue         = models.FloatField()
    wed         = models.FloatField()
    thu         = models.FloatField()
    fri         = models.FloatField()
    sat         = models.FloatField()
    sun         = models.FloatField()
    createdAt   = models.DateTimeField(auto_now_add=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return str(self.item)

    class Meta:
        verbose_name = 'Item Weekly Avg'
        verbose_name_plural = 'Item Weekly Avg'

#Order Model
class Order(models.Model):
    token           = models.UUIDField(default= uuid.uuid4)
    store           = models.ForeignKey(Store, on_delete=models.CASCADE)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory     = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    is_placed       = models.BooleanField(default = False)
    activate_day    = models.CharField(max_length=255)
    order_type      = models.CharField(max_length=255, choices=(('Prediction','Prediction'),('Custom','Custom')),default = 'Prediction')
    createdAt       = models.DateTimeField(auto_now_add=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return str(self.store)+' - '+str(self.category)+' - '+str(self.subcategory)+' - '+str(self.createdAt)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

#Order Item Model
class OrederItem(models.Model):
    order           = models.ForeignKey(Order, on_delete=models.CASCADE)
    item            = models.ForeignKey(Item, on_delete=models.CASCADE)
    total_quantity  = models.IntegerField()
    on_hand_quanty  = models.IntegerField()
    order_quantity  = models.IntegerField()
    moq             = models.IntegerField()
    createdAt       = models.DateTimeField(auto_now_add=True, null=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return str(self.item)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'


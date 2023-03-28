from datetime import datetime, timedelta
from django import template
from django.utils.timesince import timesince
from django.contrib.auth.models import Group
from django.conf import settings
from app.models import Store

register = template.Library()

@register.filter(name='addclass')
def addclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})

@register.simple_tag
def store_info(request):
    return Store.objects.filter(user=request.user).first()
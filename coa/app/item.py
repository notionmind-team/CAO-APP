from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import  HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.cache  import cache_control
from django.contrib.auth.models import User
from .models import *
from .forms import *
import logging
from datetime import date
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
db_logger = logging.getLogger('frontend')

#check user is client or not
def is_client(user):
    return user.groups.filter(name='Client').exists()

#item listing
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def item_list(request, template_name='item/list.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        item_Post = []
        #get post
        if request.method == 'POST':
            
            search_action  = request.POST['search_action'] if request.POST['search_action'] else ''
            
            if search_action == 'clear':
                #clear form
                if 'item-search-post' in request.session:
                    del request.session['item-search-post']
                return redirect('/item/listing')
            else:
                request.session['item-search-post']   = request.POST
                item_Post                             = request.POST
        else:
            if 'item-search-post' in request.session:
                item_Post = request.session['item-search-post']
            else:
                item_Post = []

        #generate default query
        complexQuery        = Q(store=store)
        if item_Post:
            
            category        = item_Post['category'] if item_Post['category'] else ''
            subcategory     = item_Post['subcategory'] if item_Post['subcategory'] else ''
            search          = item_Post['search'] if item_Post['search'] else ''
            
            if search:
                complexQuery.add(Q(sku__icontains=search) | Q(name__icontains=search), complexQuery.AND)
            if category:
                complexQuery.add(Q(category_id=category), complexQuery.AND)
            if subcategory:
                complexQuery.add(Q(subcategory_id=subcategory), complexQuery.AND)
        
        order_by    = request.GET.get('order_by')
        direction   = request.GET.get('direction')
        ordering    = order_by

        if direction == 'desc':
            ordering = '-{}'.format(ordering)

        if ordering is None:
            order_by    = 'sku'
            direction   = 'asc'
            ordering    = order_by
        
        item_list   = Item.objects.filter(complexQuery).order_by(ordering)
        paginator   = Paginator(item_list, 50)
        page        = request.GET.get('page')
        items       = paginator.get_page(page)
        data = {}
        data['object_list'] = items
        data['item_Post']   = item_Post
        data['categories']  = Category.objects.all().order_by('name')
        subcategories = []
        if 'category' in item_Post:
            if item_Post['category']:
                subcategories  = Subcategory.objects.filter(category_id=item_Post['category']).order_by('name')
        else:
            subcategories  = []
        data['subcategories'] = subcategories
        data['order_by']  = order_by
        data['direction'] = direction
        return render(request, template_name, data)

    except Exception as e:
            db_logger.exception(e)
            return e

#item listing
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_item_status(request):
    try:
        store = Store.objects.filter(user=request.user).first()
        if request.method == 'POST':
            ids         = request.POST.getlist('records')
            items       = Item.objects.filter(store=store, token__in = ids)
            #record_ids
            for item in items:
                item.delete()
            #message
            messages.success(request,"Selected items has been successfully deleted.")
            return redirect('/item/listing')
        else:    
            #message
            messages.error(request,"Please select item(s) for deleting.")
            return redirect('/item/listing')

    except Exception as e:
            db_logger.exception(e)
            return e

#item view
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def item_view(request, token, template_name='item/detail.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        item = get_object_or_404(Item, token=token, store=store)
        return render(request, template_name, {'object':item})
    except Exception as e:
            db_logger.exception(e)
            return e

#item create
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def item_create(request, template_name='item/add.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = ItemForm(request.POST, request.FILES, store=store)
            if form.is_valid():
                form.save()
                messages.success(request,"Item has been successfully added.")
                return redirect('/item/listing')
        else:
            
            form = ItemForm(request.POST or None, store=store)
            
        return render(request, template_name, {'form':form})
    except Exception as e:
            db_logger.exception(e)
            return e

#item update
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def item_update(request, token, template_name='item/edit.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        item = get_object_or_404(Item, token=token, store=store)
        if request.method == 'POST':
            form = ItemForm(request.POST, request.FILES, instance=item, store=store)
            if form.is_valid():
                form.save()
                messages.success(request,"Item has been successfully updated.")
                return redirect('/item/listing')
        else:
            form  = ItemForm(request.POST or None, instance=item, store=store)

        return render(request, template_name, {'form':form})
    except Exception as e:
            db_logger.exception(e)
            return e

#item delete
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def item_delete(request, token, template_name='item/confirm_delete.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        item = get_object_or_404(Item, token=token, store=store)    
        if request.method=='POST':
            item.delete()
            messages.success(request,"Item has been successfully deleted.")
            return redirect('/item/listing')
        return render(request, template_name, {'object':item})
    except Exception as e:
            db_logger.exception(e)
            return e
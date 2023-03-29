from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, logout, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import  HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.cache  import cache_control
from django.contrib.auth.models import User
from .models import *
from .forms import *
from .stats import generate_charts, generate_statistics
import logging
from datetime import date
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Sum
from django.core.paginator import Paginator
from django.db.models import Q
import json
import xlwt
import pandas as pd
import numpy as np
db_logger = logging.getLogger('frontend')

#check user is client or not
def is_client(user):
    return user.groups.filter(name='Client').exists()

#login view
def login_view(request):
    try:
        #already login user
        if request.user.is_authenticated:
                return redirect('/dashboard')
        #check post login user
        if request.method == 'POST':
            print(request.POST)
            form = LoginForm(request, data=request.POST)
            if form.is_valid():
                print("valid")
                username = request.POST['username']
                password = request.POST['password']
  
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    db_logger.info(str(username)+" is successfully login")
                    return redirect('/dashboard')
                else:
                    db_logger.warning(str(username)+" is not found")
                    messages.error(request, str(username)+" is not found")
                    return redirect('/login')
        else:
            form = LoginForm()  
        
        context = {"form": form,}
        return render(request, 'login.html', context)

    except Exception as e:
            db_logger.exception(e)
            return e

# - logout page
@login_required(login_url='/login') # - if not logged in redirect to /
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    try:
        username = request.user.email
        logout(request)
        db_logger.info(str(username)+" is successfully logout")
        return HttpResponseRedirect('/login')
    except Exception as e:
            db_logger.exception(e)
            return e

#Dashboard
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    try:
        context             = {}
        store               = Store.objects.filter(user=request.user).first()
        chart4_labels       = []
        chart4_values       = []
        chart1_w1_values    = [0,0,0,0,0,0,0]
        chart1_w2_values    = [0,0,0,0,0,0,0]
        chart2_w1_values    = [0,0,0,0,0,0,0]
        chart2_w2_values    = [0,0,0,0,0,0,0]

        if store:
            charts  = Salescharts.objects.filter(store=store).first()

            if charts:

                if charts.chart1['primary_data']:

                    for k,j in charts.chart1['primary_data']:
                        try:
                            chart1_w1_values[k] = j
                        except Exception as e:
                            chart1_w1_values[k] = 0
                
                if charts.chart1['secondary_data']:

                    for k,j in charts.chart1['secondary_data']:
                        try:
                            chart1_w2_values[k] = j
                        except Exception as e:
                            chart1_w2_values[k] = 0

                if charts.chart2['primary_data']:

                    for k,j in charts.chart2['primary_data']:
                        try:
                            chart2_w1_values[k] = round(j,2)
                        except Exception as e:
                            chart2_w1_values[k] = 0
                
                if charts.chart2['secondary_data']:

                    for k,j in charts.chart2['secondary_data']:
                        try:
                            chart2_w2_values[k] = round(j,2)
                        except Exception as e:
                            chart2_w2_values[k] = 0
                
                if charts.chart3['data']:
                    for item in charts.chart3['data']:

                        itemdata  = Item.objects.filter(store=store, sku = item[0]).first()
                        if itemdata.image:
                            item.append(itemdata.image.url)
                        else:
                            item.append('')

                if charts.chart4['data']:
                    for item in charts.chart4['data']:
                        chart4_labels.append(item[1])
                        chart4_values.append(round(item[2],2))
                
                context['charts']               = charts
                context['chart4_len']           = len(chart4_labels)
                context['chart1_w1_values']     = json.dumps(chart1_w1_values)
                context['chart1_w2_values']     = json.dumps(chart1_w2_values)
                context['chart2_w1_values']     = json.dumps(chart2_w1_values)
                context['chart2_w2_values']     = json.dumps(chart2_w2_values)
                context['chart4_labels']        = json.dumps(chart4_labels)
                context['chart4_values']        = chart4_values
                context['store']                = store


        return render(request, 'dashboard.html', context)
    except Exception as e:
        db_logger.exception(e)
        return e

#prediction
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def prediction(request):
    try:
        store           = Store.objects.filter(user=request.user).first()
        #get post
        if request.method == 'POST':
            
            search_action  = request.POST['search_action'] if request.POST['search_action'] else ''
            
            if search_action == 'clear':
                #clear form
                if 'prediction-search-post' in request.session:
                    del request.session['prediction-search-post']
                return redirect('/prediction')
            else:
                request.session['prediction-search-post']   = request.POST
                prediction_Post                             = request.POST
        else:
            if 'prediction-search-post' in request.session:
                prediction_Post = request.session['prediction-search-post']
            else:
                prediction_Post = []

        if 'preview_order_post' in request.session:
            preview_order_post = request.session['preview_order_post']
        else:
            preview_order_post = []
        
        current_date    = datetime.today()
        sales_data      = []
        sub_cat_info    = []
        #generate default query
        if 'category' in prediction_Post and 'subcategory' in prediction_Post:
            
            category        = prediction_Post['category'] if prediction_Post['category'] else ''
            subcategory     = prediction_Post['subcategory'] if prediction_Post['subcategory'] else ''
            if category and subcategory:
                sub_cat_info    = Subcategory.objects.filter(pk=subcategory).first()
                sales_data      = WeeklySales.objects.filter(store=store, category_id=category, subcategory_id=subcategory).last()
                if sales_data:
                    items           = WeeklyItemsAvg.objects.filter(salesweek=sales_data)
                    for item in items:
                        item.mon_quantity   = round(item.wed + item.thu + item.fri)
                        item.mon_selected   = False
                        item.mon_on_hand    = ''
                        item.mon_on_order   = 0
                        item.fri_quantity   = round(item.sat + item.sun + item.mon + item.tue)
                        item.fri_selected   = False
                        item.fri_on_hand    = ''
                        item.fri_on_order   = 0
                        if preview_order_post:
                            if preview_order_post['items']:
                                for post_item in preview_order_post['items']:
                                    if item.id == int(post_item['id']):
                                        if preview_order_post['activate_day'] == 'mon':
                                            item.mon_selected = True
                                            item.mon_on_hand  = post_item['on_hand_quanty']
                                            item.mon_on_order = post_item['order']
                                        else:
                                            item.fri_selected = True
                                            item.fri_on_hand  = post_item['on_hand_quanty']
                                            item.fri_on_order = post_item['order']
                    sales_data.items = items

        current_day         = current_date.strftime("%a").lower()
        mon_activate_days   = ['mon']
        fri_activate_days   = ['tue','wed','thu']

        if current_day in mon_activate_days:
            activate_day = 'mon'
        elif current_day in fri_activate_days:
            activate_day = 'fri'
        else:
            activate_day = None
        
        data = {}
        data['activate_day']        = activate_day
        data['object']              = sales_data
        data['prediction_Post']     = prediction_Post
        data['categories']          = Category.objects.all().order_by('name')
        subcategories = []
        if 'category' in prediction_Post:
            if prediction_Post['category']:
                subcategories  = Subcategory.objects.filter(category_id=prediction_Post['category']).order_by('name')
        else:
            subcategories           = []
        data['subcategories']       = subcategories
        data['sub_cat_info']        = sub_cat_info
        data['preview_order_post']  = preview_order_post
        return render(request, 'order/prediction.html', data)

    except Exception as e:
        db_logger.exception(e)
        return e

#order clear
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_clear(request):
    try:
        
        if 'preview_order_post' in request.session:
            del request.session['preview_order_post']
        return redirect('/prediction')

    except Exception as e:
        db_logger.exception(e)
        return e

#order preview
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_preview(request):
    try:
        data = {}
        if request.method == 'POST':
            
            items = []
            activate_day  = request.POST['activate_day'] if request.POST['activate_day'] else ''
            weeklysales   = request.POST['weeklysales'] if request.POST['weeklysales'] else ''
            ids  = request.POST.getlist('records')
            for id in ids:
                item = {}
                item['id'] = id
                if activate_day == 'mon':
                    item['order_quantity']  = request.POST['mon_order_quantity_'+str(id)]
                    item['on_hand_quanty']  = request.POST['mon_on_hand_quanty_'+str(id)]
                    item['order']           = request.POST['mon_order_'+str(id)]
                    item['moq']             = request.POST['mon_moq_'+str(id)]
                else:
                    item['order_quantity']  = request.POST['fri_order_quantity_'+str(id)]
                    item['on_hand_quanty']  = request.POST['fri_on_hand_quanty_'+str(id)]
                    item['order']           = request.POST['fri_order_'+str(id)]
                    item['moq']             = request.POST['fri_moq_'+str(id)]
                items.append(item)

            preview_order_post = {}
            preview_order_post['activate_day'] = activate_day
            preview_order_post['weeklysales']  = weeklysales
            preview_order_post['items']        = items
            
            request.session['preview_order_post'] = preview_order_post
            return redirect('/preview')

        else:

            if 'preview_order_post' in request.session:
                preview_order_post = request.session['preview_order_post']
            else:
                preview_order_post = []

        if preview_order_post:
            
            items           = preview_order_post['items']
            weeklysales     = preview_order_post['weeklysales'] if preview_order_post['weeklysales'] else ''
            activate_day    = preview_order_post['activate_day'] if preview_order_post['activate_day'] else ''
            sales_data      = WeeklySales.objects.filter(id=weeklysales).first()
            if items:
                for item in items:
                    salesinfo           = get_object_or_404(WeeklyItemsAvg, pk=item['id'])
                    item['sales_info']  = salesinfo
                    item['item_info']   = get_object_or_404(Item, pk=salesinfo.item.id)
            
            data['activate_day']  = activate_day
            data['object']        = sales_data
            data['items']         = items
            
            return render(request, 'order/preview.html', data)

        else:
            if 'preview_order_post' in request.session:
                del request.session['preview_order_post']
            return redirect('/prediction')

    except Exception as e:
        db_logger.exception(e)
        return e

#order place
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_place(request):
    try:
        
        if 'preview_order_post' in request.session:

            preview_order_post = request.session['preview_order_post']

        else:

            preview_order_post = []

        if preview_order_post:
            
            
            items               = preview_order_post['items']
            weeklysales         = preview_order_post['weeklysales'] if preview_order_post['weeklysales'] else ''
            activate_day        = preview_order_post['activate_day'] if preview_order_post['activate_day'] else ''
            sales_data          = WeeklySales.objects.filter(id=weeklysales).first()

            #save order
            order                   = Order()
            order.store             = sales_data.store
            order.category_id       = sales_data.category
            order.subcategory_id    = sales_data.subcategory
            order.activate_day      = activate_day
            order.save()

            #save order items
            if items:
                for item in items:
                    salesinfo                   = get_object_or_404(WeeklyItemsAvg, pk=item['id'])
                    order_item                  = OrederItem()
                    order_item.order            = order
                    order_item.item             = salesinfo.item
                    order_item.total_quantity   = item['order_quantity']
                    order_item.on_hand_quanty   = item['on_hand_quanty']
                    order_item.order_quantity   = item['order']
                    order_item.moq              = item['moq']
                    order_item.save()
            
            if 'prediction-search-post' in request.session:
                    del request.session['prediction-search-post']
            del request.session['preview_order_post']
            messages.success(request,"Your order has been Generated.")
            
            return redirect('/history')

        else:
            
            return redirect('/prediction')

    except Exception as e:
        db_logger.exception(e)
        return e

#order history
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_history(request):
    try:
        store        = Store.objects.filter(user=request.user).first()
        order_Post   = []
        #get post
        if request.method == 'POST':
            
            search_action  = request.POST['search_action'] if request.POST['search_action'] else ''
            
            if search_action == 'clear':
                #clear form
                if 'order-search-post' in request.session:
                    del request.session['order-search-post']
                return redirect('/history')
            else:
                request.session['order-search-post']   = request.POST
                order_Post                             = request.POST
        else:
            if 'order-search-post' in request.session:
                order_Post = request.session['order-search-post']
            else:
                order_Post = []

        #generate default query
        complexQuery        = Q(store=store)
        if order_Post:
            
            category        = order_Post['category'] if order_Post['category'] else ''
            subcategory     = order_Post['subcategory'] if order_Post['subcategory'] else ''
            
            if category:
                complexQuery.add(Q(category_id=category), complexQuery.AND)
            if subcategory:
                complexQuery.add(Q(subcategory_id=subcategory), complexQuery.AND)
            
        order_list  = Order.objects.filter(complexQuery).order_by('-createdAt')
        paginator   = Paginator(order_list, 25)
        page        = request.GET.get('page')
        items       = paginator.get_page(page)
        data = {}
        data['object_list'] = items
        data['order_Post']  = order_Post
        data['categories']  = Category.objects.all().order_by('name')
        subcategories       = []
        if 'category' in order_Post:
            if order_Post['category']:
                subcategories  = Subcategory.objects.filter(category_id=order_Post['category']).order_by('name')
        else:
            subcategories  = []
        data['subcategories']   = subcategories
        data['suppliers']       = Supplier.objects.all().order_by('name')
        return render(request, 'order/history.html', data)

    except Exception as e:
        db_logger.exception(e)
        return e

#order view
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_view(request, token):
    try:
        store           = Store.objects.filter(user=request.user).first()
        data            = {}
        data['object']  = get_object_or_404(Order, token=token, store=store)
        return render(request, 'order/order.html', data)

    except Exception as e:
        db_logger.exception(e)
        return e

#statistics
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def statistics(request):
    try:
        store           = Store.objects.filter(user=request.user).first()
        #get post
        if request.method == 'POST':
            
            search_action  = request.POST['search_action'] if request.POST['search_action'] else ''
            
            if search_action == 'clear':
                #clear form
                if 'statistics-search-post' in request.session:
                    del request.session['statistics-search-post']
                return redirect('/statistics')
            else:
                request.session['statistics-search-post']   = request.POST
                statistics_Post                             = request.POST
        else:
            if 'statistics-search-post' in request.session:
                statistics_Post = request.session['statistics-search-post']
            else:
                statistics_Post = []

        sales_data = []
        sub_cat_info = []
        #generate default query
        if 'category' in statistics_Post and 'subcategory' in statistics_Post:
            
            category        = statistics_Post['category'] if statistics_Post['category'] else ''
            subcategory     = statistics_Post['subcategory'] if statistics_Post['subcategory'] else ''
            if category and subcategory:
                sub_cat_info    = Subcategory.objects.filter(pk=subcategory).first()
                sales_data      = WeeklySales.objects.filter(store=store, category_id=category, subcategory_id=subcategory).last()
                if sales_data:
                    total_avg   = 0
                    total_ratio = 0
                    items = WeeklyItemsAvg.objects.filter(salesweek=sales_data)
                    if items:
                        for sd in items:
                            total_avg   = total_avg + sd.avg
                            total_ratio = total_ratio + sd.ratio

                    sales_data.total_avg = total_avg
                    sales_data.total_ratio = total_ratio
        data = {}
        data['object']              = sales_data
        data['statistics_Post']     = statistics_Post
        data['categories']          = Category.objects.all().order_by('name')
        subcategories = []
        if 'category' in statistics_Post:
            if statistics_Post['category']:
                subcategories  = Subcategory.objects.filter(category_id=statistics_Post['category']).order_by('name')
        else:
            subcategories       = []
        data['subcategories']   = subcategories
        data['sub_cat_info']    = sub_cat_info

        data['charts']  = Salescharts.objects.filter(store=store).first()
        
        return render(request, 'order/statistics.html', data)
        
    except Exception as e:
        db_logger.exception(e)
        return e

#subcategories
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def subcategories(request, pk):
    try:
        categories  = Subcategory.objects.filter(category_id=pk).order_by('name')  
        option_list = '<option value="">-- Select Sub Category --</option>'
        for category in categories:
             option_list += '<option value="'+str(category.id)+'">'+str(category.name)+'</option>'
        return HttpResponse(str(option_list))
    except Exception as e:
            db_logger.exception(e)
            return e

#Settings
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def store(request, template_name='store.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = StoreForm(request.POST, instance=store, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request,"Store has been successfully updated.")
                return redirect('/store')
        else:
            form = StoreForm(request.POST or None, instance=store, user=request.user)
        return render(request, template_name, {'form':form})
    
    except Exception as e:
            db_logger.exception(e)
            return e

#generate store prediction data
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generate_store_prediction_data(request):
    try:
        stores = Store.objects.filter(user=request.user).order_by('id')
        if stores:
            for store in stores:
                categories  = Category.objects.all().order_by('name')
                if categories:
                    for category in categories:
                        subcategories = Subcategory.objects.filter(category=category).order_by('name')
                        if subcategories:
                            for sub in subcategories:
                                #generate data
                                data = generate_statistics(store,category,sub)
                
                #generate charts
                charts = generate_charts(store)
        
        messages.success(request,"Store sales prediction data has been successfully.")
        return redirect('/statistics')

    except Exception as e:
            print("error => ",e)

            db_logger.exception(e)
            messages.error(request,"Error Computing Sales Prediction. Kindly verify the Sales Data")
            return redirect('/statistics')

#change order status listing
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_order_status(request):
    try:
        store = Store.objects.filter(user=request.user).first()
        if request.method == 'POST':
            ids         = request.POST.getlist('records')
            orders      = Order.objects.filter(store=store, token__in = ids)
            #record_ids
            for order in orders:
                order.is_placed = True
                order.save()
            #message
            messages.success(request,"Selected orders has been successfully placed.")
            return redirect('/history')
        else:    
            #message
            messages.error(request,"Please select order(s) for deleting.")
            return redirect('/history')

    except Exception as e:
            db_logger.exception(e)
            return e

#order download
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_download(request, token):
    try:
        store  = Store.objects.filter(user=request.user).first()
        order  = get_object_or_404(Order, token=token, store=store)
        
        
        filename    = str(store.name)+'-'+str(order.token)+'.xls'
        response    = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="'+str(filename)+'"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Order Details')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        alignment = xlwt.Alignment()
        alignment.horz = alignment.HORZ_LEFT
        alignment.vert = alignment.VERT_TOP
        alignment.wrap = alignment.WRAP_AT_RIGHT
        style_text_align_vert_center_horiz_center   = xlwt.easyxf('align: vert centre, horiz centre; font: bold on')
        
        ws.write(0, 0, str(store.name),style_text_align_vert_center_horiz_center)
        ws.merge(0, 0, 0, 5)

        row_num += 1
        
        columns = ['Category',str(order.category),'Sub Category',str(order.subcategory)]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        row_num += 1

        if order.order_type == 'Custom':
            columns = ['SKU ID','SKU Name','Supplier','Quantity']
        else:
            columns = ['SKU ID','SKU Name','Supplier','Quantity required','On Hand Quantity','Order']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        rows = OrederItem.objects.filter(order=order)
        for row in rows:
            row_num += 1
            sku_id = ''
            if row.item.sku is not None:
                sku_id   = row.item.sku
            sku_name = ''
            if row.item.name is not None:
                sku_name   = row.item.name
            supplier = ''
            if row.item.supplier is not None:
                supplier   = row.item.supplier.name

            if order.order_type == 'Custom':
                columns = [sku_id,sku_name,supplier,row.order_quantity]
            else:
                columns = [sku_id,sku_name,supplier,row.total_quantity,row.on_hand_quanty,row.order_quantity]

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
        
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

    
        wb.save(response)
        return response


    except Exception as e:
        db_logger.exception(e)
        return e

#order add new
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_add_new(request):
    try:
        store           = Store.objects.filter(user=request.user).first()
        
        #get post
        if request.method == 'POST':
            
            search_action  = request.POST['search_action'] if request.POST['search_action'] else ''
            
            if search_action == 'clear':
                #clear form
                if 'order-new-search-post' in request.session:
                    del request.session['order-new-search-post']
                
                if 'new_order_post' in request.session:
                    del request.session['new_order_post']
                
                return redirect('/add-new-order')

            else:
                request.session['order-new-search-post']   = request.POST
                Order_Post                             = request.POST
        else:
            if 'order-new-search-post' in request.session:
                Order_Post = request.session['order-new-search-post']
            else:
                Order_Post = []

        items           = []
        sub_cat_info    = []

        if 'new_order_post' in request.session:
            new_order_post = request.session['new_order_post']
        else:
            new_order_post = []

        #generate default query
        if 'category' in Order_Post and 'subcategory' in Order_Post:
            
            category        = Order_Post['category'] if Order_Post['category'] else ''
            subcategory     = Order_Post['subcategory'] if Order_Post['subcategory'] else ''
            if category and subcategory:
                sub_cat_info    = Subcategory.objects.filter(pk=subcategory).first()
                items           = Item.objects.filter(store=store, category_id=category, subcategory_id=subcategory).order_by('name')
                for item in items:
                    if new_order_post:
                        if new_order_post['items']:
                            for post_item in new_order_post['items']:
                                if item.id == int(post_item['id']):
                                    item.selected = True
                                    item.quantity  = post_item['quantity']
        
        data = {}
        data['object']         = items
        data['Order_Post']     = Order_Post
        data['categories']     = Category.objects.all().order_by('name')
        subcategories = []
        if 'category' in Order_Post:
            if Order_Post['category']:
                subcategories  = Subcategory.objects.filter(category_id=Order_Post['category']).order_by('name')
        else:
            subcategories       = []
        data['subcategories']   = subcategories
        data['sub_cat_info']    = sub_cat_info
        data['new_order_post']  = new_order_post
        

        return render(request, 'order/new.html', data)
    except Exception as e:
        db_logger.exception(e)
        return e

#order preview
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_add_new_preview(request):
    try:
        store           = Store.objects.filter(user=request.user).first()
        data            = {}

        if 'order-new-search-post' in request.session:
            Order_Post = request.session['order-new-search-post']
        else:
            Order_Post = []

        if request.method == 'POST':
            items = []
            ids  = request.POST.getlist('records')

            if 'records' in request.POST:
                
                for id in ids:
                    item = {}
                    item['id'] = id
                    item['quantity']  = request.POST['quantity_'+str(id)]
                    items.append(item)
                
                new_order_post = {}
                new_order_post['items']             = items
                request.session['new_order_post']   = new_order_post
                return redirect('/add-new-order/preview')
            
            else:

                messages.error(request,"Please select atleast one item for order.")
                return redirect('/add-new-order')


        else:

            if 'new_order_post' in request.session:
                new_order_post = request.session['new_order_post']
            else:
                new_order_post = []

        if new_order_post:
            
            items           = new_order_post['items']
            if items:
                for item in items:
                    item['item_info']   = get_object_or_404(Item, pk=item['id'])
            
            data['items']         = items
            data['object']        = store
            data['sub_cat_info']  = Subcategory.objects.filter(pk=Order_Post['subcategory']).first()
            
            return render(request, 'order/new-preview.html', data)

        else:
            if 'new_order_post' in request.session:
                del request.session['new_order_post']
            return redirect('/add-new-order')

    except Exception as e:
        db_logger.exception(e)
        return e

#order new place
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_add_new_generate(request):
    try:
        
        store           = Store.objects.filter(user=request.user).first()
        Order_Post      = request.session['order-new-search-post']

        if 'new_order_post' in request.session:

            new_order_post = request.session['new_order_post']

        else:

            new_order_post = []

        if new_order_post:
            
            current_date        = datetime.today()
            current_day         = current_date.strftime("%a").lower()
            items               = new_order_post['items']

            order                   = Order()
            order.store             = store
            order.category_id       = Order_Post['category']
            order.subcategory_id    = Order_Post['subcategory']
            order.activate_day      = current_day
            order.order_type        = 'Custom'
            order.save()

            #save order items
            if items:
                for item in items:
                    iteminfo                    = get_object_or_404(Item, pk=item['id'])
                    order_item                  = OrederItem()
                    order_item.order            = order
                    order_item.item             = iteminfo
                    order_item.total_quantity   = 0
                    order_item.on_hand_quanty   = 0
                    order_item.moq              = 0
                    order_item.order_quantity   = item['quantity']
                    order_item.save()
            
            if 'order-new-search-post' in request.session:
                    del request.session['order-new-search-post']
            del request.session['new_order_post']
            messages.success(request,"Your order has been Generated.")
            
            return redirect('/history')

        else:
            
            return redirect('/add-new-order')

    except Exception as e:
        db_logger.exception(e)
        return e

#subcategories
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_chart_data(request, token, cid):
    try:

        store           = Store.objects.filter(user=request.user, token=token).first()
        charts          = Salescharts.objects.filter(store=store).first()
        chart_labels    = []
        chart_values    = []

        if int(cid) == 1:
            if charts.chart4['data']:
                for item in charts.chart4['data']:
                    chart_labels.append(item[1])
                    chart_values.append(round(item[2],2))
        elif int(cid) == 2:
            if charts.chart5['data']:
                for item in charts.chart5['data']:
                    chart_labels.append(item[0])
                    chart_values.append(round(item[1],2))
        elif int(cid) == 3:
            if charts.chart6['data']:
                for item in charts.chart6['data']:
                    chart_labels.append(item[0])
                    chart_values.append(round(item[1],2))

        data = [{'labels': chart_labels, 'values': chart_values}]

        return JsonResponse(data, safe=False)
    
    except Exception as e:
            db_logger.exception(e)
            return e
        
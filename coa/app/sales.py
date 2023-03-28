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
import os
import datetime
import pandas as pd
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
db_logger = logging.getLogger('frontend')

#check user is client or not
def is_client(user):
    return user.groups.filter(name='Client').exists()

#check date is valid or not
def is_date_valid(obj):
    return isinstance(obj, datetime.date)

#sales listing
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_list(request, template_name='sales/list.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        if 'import-filename' in request.session:
                if os.path.exists('media/salesdata/'+str(request.session['import-filename'])):
                    os.remove('media/salesdata/'+str(request.session['import-filename']))
                del request.session['import-filename']

        sales_Post = []
        #get post
        if request.method == 'POST':
            
            search_action  = request.POST['search_action'] if request.POST['search_action'] else ''
            
            if search_action == 'clear':
                #clear form
                if 'sales-search-post' in request.session:
                    del request.session['sales-search-post']
                return redirect('/sales/listing')
            else:
                request.session['sales-search-post']   = request.POST
                sales_Post                             = request.POST
        else:
            if 'sales-search-post' in request.session:
                sales_Post = request.session['sales-search-post']
            else:
                sales_Post = []

        #generate default query
        complexQuery        = Q(item__store=store)
        if sales_Post:
            
            category        = sales_Post['category'] if sales_Post['category'] else ''
            subcategory     = sales_Post['subcategory'] if sales_Post['subcategory'] else ''
            search          = sales_Post['search'] if sales_Post['search'] else ''
            from_date       = sales_Post['from_date'] if sales_Post['from_date'] else ''
            to_date         = sales_Post['to_date'] if sales_Post['to_date'] else ''
            
            if search:
                complexQuery.add(Q(item__sku__icontains=search) | Q(item__name__icontains=search), complexQuery.AND)
            if category:
                complexQuery.add(Q(item__category_id=category), complexQuery.AND)
            if subcategory:
                complexQuery.add(Q(item__subcategory_id=subcategory), complexQuery.AND)
            
            if from_date and to_date:
                complexQuery.add(Q(updatedOn__gte=from_date) & Q(updatedOn__lte=to_date), complexQuery.AND)
            elif from_date:
                complexQuery.add(Q(updatedOn=from_date), complexQuery.AND)
            elif to_date:
                complexQuery.add(Q(updatedOn=to_date), complexQuery.AND)

        order_by    = request.GET.get('order_by')
        direction   = request.GET.get('direction')

        if order_by == 'sku':
            ordering = 'item__sku'
        elif order_by == 'name':
            ordering = 'item__name'
        else:
            ordering = order_by
        
        if direction == 'desc':
            ordering = '-{}'.format(ordering)

        if ordering is None:
            order_by    = 'updatedOn'
            direction   = 'asc'
            ordering    = order_by
        
        sales_list  = Sales.objects.filter(complexQuery).order_by(ordering)
        paginator   = Paginator(sales_list, 50)
        page        = request.GET.get('page')
        saless      = paginator.get_page(page)
        data = {}
        data['object_list'] = saless
        data['sales_Post']  = sales_Post
        data['categories']  = Category.objects.all().order_by('name')
        subcategories = []
        if 'category' in sales_Post:
            if sales_Post['category']:
                subcategories  = Subcategory.objects.filter(category_id=sales_Post['category']).order_by('name')
        else:
            subcategories  = []
        data['subcategories'] = subcategories

        data['order_by']  = order_by
        data['direction'] = direction
        return render(request, template_name, data)

    except Exception as e:

            db_logger.exception(e)
            return e

#sales listing
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_sales_status(request):
    try:
        store = Store.objects.filter(user=request.user).first()
        if request.method == 'POST':

            if 'records' in request.POST:
                ids         = request.POST.getlist('records')
                saless      = Sales.objects.filter(item__store=store, id__in = ids)
                #record_ids
                for sales in saless:
                    sales.delete()
                #message
                messages.success(request,"Selected sales has been successfully deleted.")
                return redirect('/sales/listing')
            else:    
                #message
                messages.error(request,"Please select item(s) for deleting.")
                return redirect('/sales/listing')
        else:    
            
            return redirect('/sales/listing')

    except Exception as e:
            db_logger.exception(e)
            return e

#sales view
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_view(request, pk, template_name='sales/detail.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        sales = get_object_or_404(Sales, pk=pk, item__store=store)
        return render(request, template_name, {'object':sales})
    except Exception as e:
            db_logger.exception(e)
            return e

#sales create
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_create(request, template_name='sales/add.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = SalesForm(request.POST, store=store)
            if form.is_valid():
                salesdata           = form.save()
                salesdata.revenue   = salesdata.quantity * salesdata.item.price
                salesdata.save()
                messages.success(request,"Sales has been successfully added.")
                return redirect('/sales/listing')
        else:
            
            form = SalesForm(request.POST or None, store=store)
            
        return render(request, template_name, {'form':form})
    except Exception as e:
            db_logger.exception(e)
            return e

#sales update
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_update(request, pk, template_name='sales/edit.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        sales = get_object_or_404(Sales, pk=pk, item__store=store)
        if request.method == 'POST':
            form = SalesForm(request.POST, instance=sales, store=store)
            if form.is_valid():
                salesdata           = form.save()
                salesdata.revenue   = salesdata.quantity * salesdata.item.price
                salesdata.save()
                messages.success(request,"Sales has been successfully updated.")
                return redirect('/sales/listing')
        else:
            form  = SalesForm(request.POST or None, instance=sales, store=store)

        return render(request, template_name, {'form':form})
    except Exception as e:
            db_logger.exception(e)
            return e

#sales delete
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_delete(request, pk, template_name='sales/confirm_delete.html'):
    try:
        store = Store.objects.filter(user=request.user).first()
        sales = get_object_or_404(Sales, pk=pk, item__store=store)    
        if request.method=='POST':
            sales.delete()
            messages.success(request,"Sales has been successfully deleted.")
            return redirect('/sales/listing')
        return render(request, template_name, {'object':sales})
    except Exception as e:
            db_logger.exception(e)
            return e

#sales data import
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_import_upload(request, template_name='sales/import/upload.html'):
    try:
        context         = {}
        store           = Store.objects.filter(user=request.user).first()
        ALLOWED_TYPES   = ['xls', 'xlsx', 'XLS', 'XLSX']

        if 'import-filename' in request.session:
                if os.path.exists('media/salesdata/'+str(request.session['import-filename'])):
                    os.remove('media/salesdata/'+str(request.session['import-filename']))
                del request.session['import-filename']
        
        if request.method == 'POST':
            
            if request.FILES:
                file_list = request.FILES.get('import', None)    
                try:
                    extension = os.path.splitext(file_list.name)[1][1:].lower()

                    if extension in ALLOWED_TYPES:

                        if file_list.multiple_chunks():
                            messages.error(request,"Uploaded file is too big (%.2f MB)." % (file_list.size/(1000*1000),))
                            return redirect('/sales/import/upload')
                        
                        myfile      = request.FILES['import']
                        fs          = FileSystemStorage('media/salesdata/')
                        filename    = fs.save(myfile.name, myfile)
                        request.session['import-filename'] = filename
                        return redirect('/sales/import/list')

                    else:
                        messages.error(request, 'File types is not allowed')
                        return redirect('/sales/import/upload')
                except Exception as e:
                    db_logger.exception(e)
                    messages.error(request, 'Can not identify file type : '+str(e))
                    return redirect('/sales/import/upload')
            else:
                messages.error(request, 'Please Select File')
                return redirect('/sales/import/upload')
            
        return render(request, template_name,context)
    except Exception as e:
            db_logger.exception(e)
            return e


#vendor import list
@login_required(login_url='/login') # - if not logged in redirect to /
@user_passes_test(is_client, login_url='/logout') # - if not admin, redirect to login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_import_list(request, template_name='sales/import/list.html'):
    context         = {}
    records         = []
    headers         = []
    try:
        if 'import-filename' in request.session:

            store       = Store.objects.filter(user=request.user).first()
            filename    = request.session.get('import-filename')
            extension   = os.path.splitext(filename)[1][1:].lower()
            if filename.endswith('.csv'):
                df = pd.read_csv('media/salesdata/'+str(filename))
            else:
                df = pd.read_excel('media/salesdata/'+str(filename))
            
            if request.method == 'POST':
                
                updates_date_list = []

                if 'ids' in request.POST:

                    for did in request.POST.getlist('ids'):
                        did        = int(did)
                        sku_id     = df['SKU_ID'][did] if df['SKU_ID'][did] else None
                        itemdata   = Item.objects.filter(sku=sku_id, store=store).first()
                        qnty       = df['QUANTITY'][did] if df['QUANTITY'][did] else 0
                        updatedon  = df['UPDATED_ON'][did] if df['UPDATED_ON'][did] else None

                        if updatedon not in updates_date_list:
                            updates_date_list.append(updatedon)

                        if itemdata:
                            
                            sales = Sales.objects.filter(item=itemdata,updatedOn=updatedon).first()

                            if sales:
                                sales.quantity  = qnty
                                sales.save()
                            else:
                                sales           = Sales()
                                sales.item      = itemdata
                                sales.quantity  = qnty
                                sales.revenue   = qnty * itemdata.price
                                sales.updatedOn = updatedon
                                sales.save()

                    #insert empty records
                    if updates_date_list:
                        for updated in updates_date_list:
                            items = Item.objects.filter(store=store)
                            if items:
                                for item in items:
                                    if not Sales.objects.filter(item=item,updatedOn=updated).first():
                                        sales           = Sales()
                                        sales.item      = item
                                        sales.quantity  = 0
                                        sales.revenue   = 0
                                        sales.updatedOn = updated
                                        sales.save()

                    if os.path.exists('media/salesdata/'+str(request.session['import-filename'])):
                        os.remove('media/salesdata/'+str(request.session['import-filename']))
                    del request.session['import-filename']

                    messages.success(request, 'Selected item(s) has been imported successfully.')
                    return redirect('/sales/listing')

                else:

                    messages.error(request, 'Please select item(s) for import.')
                    return redirect('/sales/import/list')
            
            else:

                headers = []
                for h in df.columns:
                    headers.append(h)

                sku_id_list     = []
                header_message  = []
                header_is_valid = True
                
                if 'SKU_ID' not in headers:
                    header_message.append('SKU_ID Header not found')
                    header_is_valid = False
                
                if 'SKU_NAME' not in headers:
                    header_message.append('SKU_NAME Header not found')
                    header_is_valid = False
                
                if 'QUANTITY' not in headers:
                    header_message.append('QUANTITY Header not found')
                    header_is_valid = False

                if 'UPDATED_ON' not in headers:
                    header_message.append('UPDATED_ON Header not found')
                    header_is_valid = False

                if header_is_valid:

                    if len(df) > 0:

                        for line in range(len(df)):
                            data_dict = {}
                            data_dict['id']         = line
                            data_dict['sku_id']     = df['SKU_ID'][line] if df['SKU_ID'][line] else None
                            data_dict['sku_name']   = df['SKU_NAME'][line] if df['SKU_NAME'][line] else None
                            data_dict['qnty']       = df['QUANTITY'][line] if df['QUANTITY'][line] else 0
                            data_dict['revn']       = 0
                            data_dict['updatedon']  = df['UPDATED_ON'][line] if df['UPDATED_ON'][line] else None

                            if data_dict['sku_id'] and data_dict['sku_name'] and data_dict['qnty'] >= 0 and data_dict['updatedon']:
                                
                                if is_date_valid(data_dict['updatedon']):
                                    duplicate = str(data_dict['sku_id'])+'-'+str(data_dict['updatedon'].strftime("%Y-%m-%d"))
                                else:
                                    duplicate = str(data_dict['sku_id'])+'-'+str(data_dict['updatedon'])

                                itemdata = Item.objects.filter(sku=data_dict['sku_id'], store=store).first()
                                if itemdata:
                                    data_dict['revn'] = data_dict['qnty'] * itemdata.price

                                if not itemdata:
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     =  str(data_dict['sku_id'])+' is not found in store'
                                elif not is_date_valid(data_dict['updatedon']):
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     = 'Invalid Date or format : '+str(data_dict['updatedon'])
                                elif Sales.objects.filter(item__sku=data_dict['sku_id'], item__store=store, updatedOn=data_dict['updatedon']).first():
                                    data_dict["status"]  = 'success'
                                    data_dict["msg"]     = str(data_dict['sku_id'])+' is already imported in '+str(data_dict['updatedon'].strftime("%Y-%m-%d"))
                                elif duplicate in sku_id_list:
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     = str(data_dict['sku_id'])+' is duplicates with '+str(data_dict['updatedon'].strftime("%Y-%m-%d"))
                                elif int(data_dict['qnty']) < 0:
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     = str(data_dict['sku_id'])+' quantity in negative'
                                else:
                                    data_dict["status"]  = 'success'
                                    data_dict["msg"]     = '-'

                                sku_id_list.append(duplicate)

                            else:

                                if data_dict['sku_id'] is None:
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     = 'Item SKU_ID is None'
                                elif data_dict['sku_name'] is None:
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     = 'Item SKU_Name is None'
                                elif data_dict['qnty'] < 0:
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     = str(data_dict['sku_id'])+' quantity is negative'
                                else:
                                    data_dict["status"]  = 'error'
                                    data_dict["msg"]     =  str(data_dict['sku_id'])+' updateon date is None'
                                
                            records.append(data_dict)

                        context['records'] = records
                    else:
                        context['records'] = []
                else:
                    context['header_message'] = header_message
                    for msg in header_message:
                        messages.error(request, msg)
                    return redirect('/sales/import/upload')
                
                context['header_is_valid'] = header_is_valid

                return render(request, template_name, context)
        
        else:

            return redirect('/sales/import/upload')

    except Exception as e:
            db_logger.exception(e)
            return e
from django.urls import path, include
from django.conf.urls import url
from . import views, item, sales

urlpatterns = [
    path('', views.login_view,name='login'),
    path('login', views.login_view,name='login'),
    path('logout', views.logout_view, name='logout'),
    path('dashboard', views.dashboard,name='dashboard'),
    path('statistics', views.statistics,name='statistics'),
    path('prediction', views.prediction,name='prediction'),
    path('preview', views.order_preview,name='order_preview'),
    path('place-order', views.order_place,name='order_place'),
    path('order-clear', views.order_clear,name='order_clear'),
    path('change-order-clear', views.change_order_status,name='change_order_status'),
    path('order/<str:token>', views.order_view,name='order_view'),
    path('order-download/<str:token>', views.order_download,name='order_download'),
    path('add-new-order', views.order_add_new,name='order_add_new'),
    path('add-new-order/preview', views.order_add_new_preview,name='order_add_new_preview'),
    path('add-new-order/generate', views.order_add_new_generate,name='order_add_new_generate'),
    path('history', views.order_history,name='order_history'),
    path('store', views.store,name='store'),
    path('generate_store_prediction_data', views.generate_store_prediction_data,name='generate_store_prediction_data'),
    path('change-chart/<str:token>/<int:cid>', views.change_chart_data, name='change_chart_data'),
    #get category's subcategories
    path('subcategories/<int:pk>', views.subcategories, name='subcategories'),
    #items
    path('item/listing', item.item_list, name='item_list'),
    path('item/status', item.change_item_status, name='change_item_status'),
    path('item/view/<str:token>', item.item_view, name='item_view'),
    path('item/new', item.item_create, name='item_new'),  
    path('item/edit/<str:token>', item.item_update, name='item_edit'),
    path('item/delete/<str:token>', item.item_delete, name='item_delete'),
    #sales data
    path('sales/listing', sales.sales_list, name='sales_list'),
    path('sales/status', sales.change_sales_status, name='change_sales_status'),
    path('sales/view/<int:pk>', sales.sales_view, name='sales_view'),
    path('sales/new', sales.sales_create, name='sales_new'),  
    path('sales/edit/<int:pk>', sales.sales_update, name='sales_edit'),
    path('sales/delete/<int:pk>', sales.sales_delete, name='sales_delete'),
    path('sales/import/upload', sales.sales_import_upload, name='sales_import_upload'),
    path('sales/import/list', sales.sales_import_list, name='sales_import_list'),
] 
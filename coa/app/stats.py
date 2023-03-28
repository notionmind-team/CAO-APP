from app.models import *
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

#generate statistics
def generate_statistics(store,category,sub_category):
    start_date = datetime.today()
    #start_date = datetime.today()-timedelta(days=1)
    weeks=[]
    weeks.append((start_date,start_date-timedelta(days=6)))
    weeks.append((start_date-timedelta(days=7),start_date-timedelta(days=13)))
    weeks.append((start_date-timedelta(days=14),start_date-timedelta(days=20)))

    data_w1 = Sales.objects.filter(item__store=store, item__category=category, item__subcategory=sub_category, updatedOn__lte=weeks[0][0], updatedOn__gte=weeks[0][1])
    data_w2 = Sales.objects.filter(item__store=store, item__category=category, item__subcategory=sub_category, updatedOn__lte=weeks[1][0], updatedOn__gte=weeks[1][1])
    data_w3 = Sales.objects.filter(item__store=store, item__category=category, item__subcategory=sub_category, updatedOn__lte=weeks[2][0], updatedOn__gte=weeks[2][1])

    #this_week_all_data = Sales.objects.filter(updatedOn__lte=weeks[0][0], updatedOn__gte=weeks[0][1])

    no_of_week= np.sum([len(data_w1)>0,len(data_w2)>0,len(data_w3)>0])

    if no_of_week==0:
        return True
        
    pd_w1 = pd.DataFrame(data_w1.values('item__sku','item__name','quantity','revenue','updatedOn'))
    if len(data_w1)>0:    
        pd_w1.updatedOn = pd.to_datetime(pd_w1.updatedOn)
        pd_w1['week'] = pd_w1.updatedOn.dt.weekofyear
        pd_w1['day'] = pd_w1.updatedOn.dt.dayofweek

    pd_w2 = pd.DataFrame(data_w2.values('item__sku','item__name','quantity','revenue','updatedOn'))
    if len(data_w2)>0:
        pd_w2.updatedOn = pd.to_datetime(pd_w2.updatedOn)
        pd_w2['week'] = pd_w2.updatedOn.dt.weekofyear
        pd_w2['day'] = pd_w2.updatedOn.dt.dayofweek

    pd_w3 = pd.DataFrame(data_w3.values('item__sku','item__name','quantity','revenue','updatedOn'))
    if len(data_w3)>0:
        pd_w3.updatedOn = pd.to_datetime(pd_w3.updatedOn)
        pd_w3['week'] = pd_w3.updatedOn.dt.weekofyear
        pd_w3['day'] = pd_w3.updatedOn.dt.dayofweek

    pd_all = pd.concat([pd_w1,pd_w2,pd_w3],sort=False)

    #pd_this_week_all_data = pd.DataFrame(this_week_all_data.values('item__sku','item__name','item__category__name','item__subcategory__name','quantity','revenue','updatedOn'))
    #if len(pd_this_week_all_data)>0:
    #    pd_this_week_all_data.updatedOn = pd.to_datetime(pd_this_week_all_data.updatedOn)
    #    pd_this_week_all_data['week'] = pd_this_week_all_data.updatedOn.dt.weekofyear
    #    pd_this_week_all_data['day'] = pd_this_week_all_data.updatedOn.dt.dayofweek

    day_wise_item_wise_quan_avg = pd_all.quantity.groupby([pd_all.item__sku,pd_all.day]).mean() #/no_of_week  
    item_wise_quan_avg = pd_all.quantity.groupby([pd_all.item__sku]).mean() #/ no_of_week
    day_wise_sale_avg = pd_all.revenue.groupby([pd_all.day]).mean() #/ no_of_week
    final_day_wise_sale_avg = pd.Series([.0,.0,.0,.0,.0,.0,.0])
    for i in range(7):
        try:
            final_day_wise_sale_avg[i]=day_wise_sale_avg[i]
        except:
            pass 
    tot_weekly_sale_avg = day_wise_sale_avg.sum()  
    sku_to_sales_ratio = item_wise_quan_avg/tot_weekly_sale_avg
    day_wise_item_wise_quan_avg_ratio = pd.DataFrame(np.outer(sku_to_sales_ratio,final_day_wise_sale_avg), columns=['Mon','Tue','Wed','Thr','Fri','Sat','Sun'])
    sku_id_data = pd.DataFrame(pd_w1.item__sku.unique(),columns=['sku_id'])
    day_wise_item_wise_quan_avg_ratio = pd.concat([sku_id_data,day_wise_item_wise_quan_avg_ratio], sort=False,axis=1)
    day_wise_item_wise_quan_avg_ratio['item_wise_quan_avg']=day_wise_item_wise_quan_avg_ratio[['Mon','Tue','Wed','Thr','Fri','Sat','Sun']].sum(axis=1)
    
    #Weekly Sales Data
    ws              = WeeklySales()
    ws.store        = store
    ws.category     = category
    ws.subcategory  = sub_category

    ws.mon = final_day_wise_sale_avg[0]
    ws.tue = final_day_wise_sale_avg[1]
    ws.wed = final_day_wise_sale_avg[2]
    ws.thu = final_day_wise_sale_avg[3]
    ws.fri = final_day_wise_sale_avg[4]
    ws.sat = final_day_wise_sale_avg[5]
    ws.sun = final_day_wise_sale_avg[6]
    
    ws.tot = tot_weekly_sale_avg
    ws.save()

    for row in day_wise_item_wise_quan_avg_ratio.itertuples():
        sku              =  row.sku_id
        avg              =  row.item_wise_quan_avg
        ration           =  sku_to_sales_ratio[sku]
        wia              =  WeeklyItemsAvg()
        wia.salesweek    =  ws
        wia.item         =  Item.objects.filter(store=store, category=category, subcategory=sub_category, sku=sku).first()
        wia.avg          =  avg
        wia.ratio        =  ration
        
        try:
            wia.mon = row.Mon
        except Exception as e:
            wia.mon = 0
        
        try:
            wia.tue = row.Tue
        except Exception as e:
            wia.tue = 0
        
        try:
            wia.wed = row.Wed
        except Exception as e:
            wia.wed = 0
        
        try:
            wia.thu = row.Thr
        except Exception as e:
            wia.thu = 0
        
        try:
            wia.fri = row.Fri
        except Exception as e:
            wia.fri = 0
        
        try:
            wia.sat  = row.Sat
        except Exception as e:
            wia.sat = 0
        
        try:
            wia.sun  = row.Sun
        except Exception as e:
            wia.sun = 0
        
        wia.save()
    
    return True

#generate charts
def generate_charts(store):
    #start_date = datetime.today()-timedelta(days=1)
    start_date = datetime.today()
    weeks=[]
    weeks.append((start_date,start_date-timedelta(days=6)))
    weeks.append((start_date-timedelta(days=7),start_date-timedelta(days=13)))
    #weeks.append((start_date-timedelta(days=14),start_date-timedelta(days=20)))

    data_w1 = Sales.objects.filter(item__store=store, updatedOn__lte=weeks[0][0], updatedOn__gte=weeks[0][1])
    data_w2 = Sales.objects.filter(item__store=store, updatedOn__lte=weeks[1][0], updatedOn__gte=weeks[1][1])
    #data_w3 = Sales.objects.filter(item__store=store, updatedOn__lte=weeks[2][0], updatedOn__gte=weeks[2][1])

    this_week_all_data = Sales.objects.filter(updatedOn__lte=weeks[0][0], updatedOn__gte=weeks[0][1])

    no_of_week= np.sum([len(data_w1)>0,len(data_w2)>0])

    if no_of_week==0:
        return True
        
    pd_w1 = pd.DataFrame(data_w1.values('item__sku','item__name','quantity','revenue','updatedOn'))
    if len(data_w1)>0:    
        pd_w1.updatedOn = pd.to_datetime(pd_w1.updatedOn)
        pd_w1['week'] = pd_w1.updatedOn.dt.weekofyear
        pd_w1['day'] = pd_w1.updatedOn.dt.dayofweek

    pd_w2 = pd.DataFrame(data_w2.values('item__sku','item__name','quantity','revenue','updatedOn'))
    if len(data_w2)>0:
        pd_w2.updatedOn = pd.to_datetime(pd_w2.updatedOn)
        pd_w2['week'] = pd_w2.updatedOn.dt.weekofyear
        pd_w2['day'] = pd_w2.updatedOn.dt.dayofweek

    #pd_w3 = pd.DataFrame(data_w3.values('item__sku','item__name','quantity','revenue','updatedOn'))
    #if len(data_w3)>0:
    #    pd_w3.updatedOn = pd.to_datetime(pd_w3.updatedOn)
    #    pd_w3['week'] = pd_w3.updatedOn.dt.weekofyear
    #    pd_w3['day'] = pd_w3.updatedOn.dt.dayofweek

    pd_all = pd.concat([pd_w1,pd_w2],sort=False)

    pd_this_week_all_data = pd.DataFrame(this_week_all_data.values('item__sku','item__name','item__category__name','item__subcategory__name','quantity','revenue','updatedOn'))
    if len(pd_this_week_all_data)>0:
        pd_this_week_all_data.updatedOn = pd.to_datetime(pd_this_week_all_data.updatedOn)
        pd_this_week_all_data['week'] = pd_this_week_all_data.updatedOn.dt.weekofyear
        pd_this_week_all_data['day'] = pd_this_week_all_data.updatedOn.dt.dayofweek

    #day_wise_item_wise_quan_avg = pd_all.quantity.groupby([pd_all.item__sku,pd_all.day]).sum()/no_of_week  
    #item_wise_quan_avg = pd_all.quantity.groupby([pd_all.item__sku]).sum() / no_of_week
    #day_wise_sale_avg = pd_all.revenue.groupby([pd_all.day]).sum() / no_of_week    
    #tot_weekly_sale_avg = day_wise_sale_avg.sum()  
    #sku_to_sales_ratio = item_wise_quan_avg/tot_weekly_sale_avg
    #day_wise_item_wise_quan_avg_ratio = pd.DataFrame(np.outer(sku_to_sales_ratio,day_wise_sale_avg), columns=['Mon','Tue','Wed','Thr','Fri','Sat','Sun'])
    #sku_id_data = pd.DataFrame(pd_w1.item__sku.unique(),columns=['sku_id'])
    #day_wise_item_wise_quan_avg_ratio = pd.concat([sku_id_data,day_wise_item_wise_quan_avg_ratio], sort=False,axis=1)
    #day_wise_item_wise_quan_avg_ratio['item_wise_quan_avg']=day_wise_item_wise_quan_avg_ratio[['Mon','Tue','Wed','Thr','Fri','Sat','Sun']].sum(axis=1)
    
    chart1 ={
        'title':'DayWise Sales(Quantity)',
        'summary1':{'text':'This Week Sale','value':0},
        'summary2':{'text':'Diff in Sale','value':0},
        'primary_text':'This Week',
        'secondary_text':'Last Week',
        'primary_data':[],
        'secondary_data':[],
    }   
    chart2 ={
        'title':'DayWise Sales($)',
        'summary1':{'text':'This Week Sale','value':0},
        'summary2':{'text':'Diff in Sale','value':0},
        'primary_text':'This Week',
        'secondary_text':'Last Week',
        'primary_data':[],
        'secondary_data':[],
    }   
    chart3={
        'title':'Item Wise Sales',
        'data':[],
    }
    chart4={
        'title':'Item Wise (%) of Sales',
        'data':[]
    }
    chart5={
        'title':'Category Wise (%) of Sales',
        'data':[]
    }
    chart6={
        'title':'Sub-Category Wise (%) of Sales',
        'data':[]
    }
    if len(pd_this_week_all_data)>0:
        this_week_total_quan = pd_this_week_all_data.quantity.sum()
        this_week_cat_percentage = (pd_this_week_all_data.quantity.groupby([pd_this_week_all_data.item__category__name]).sum()/this_week_total_quan)*100
        this_week_subcat_percentage = (pd_this_week_all_data.quantity.groupby([pd_this_week_all_data.item__subcategory__name]).sum()/this_week_total_quan)*100
        pi_data=[]
        for d in this_week_cat_percentage.items():
            pi_data.append(d)
        chart5['data']=pi_data

        pi_data=[]
        for d in this_week_subcat_percentage.items():
            pi_data.append(d)
        chart6['data']=pi_data

    if len(data_w1)>0 and len(data_w2)>0:
        this_week_sale = pd_w1.revenue.groupby([pd_w1.day]).sum()
        this_week_quan = pd_w1.quantity.groupby([pd_w1.day]).sum()
        this_week_item_wise_sale = pd_w1.revenue.groupby([pd_w1.item__sku]).sum()
        this_week_item_wise_quan = pd_w1.quantity.groupby([pd_w1.item__sku]).sum()
        this_week_total_quan = pd_w1.quantity.sum()
        this_week_item_percentage = (this_week_item_wise_quan/this_week_total_quan)*100
        this_week_total_sale = pd_w1.revenue.sum()

        last_week_sale = pd_w2.revenue.groupby([pd_w2.day]).sum()
        last_week_quan = pd_w2.quantity.groupby([pd_w2.day]).sum()
        last_week_item_wise_sale = pd_w2.revenue.groupby([pd_w2.item__sku]).sum()
        last_week_total_quan = pd_w2.quantity.sum()
        last_week_total_sale = pd_w2.revenue.sum() 
        diff_total_sale = ((this_week_total_sale-last_week_total_sale)/last_week_total_sale)*100
        diff_total_quan = ((this_week_total_quan-last_week_total_quan)/last_week_total_quan)*100
        diff_item_wise = ((this_week_item_wise_sale-last_week_item_wise_sale)/last_week_item_wise_sale)*100
        
        chart1['primary_data']=list(this_week_quan.items())
        chart1['secondary_data']=list(last_week_quan.items())
        chart1['summary1']['value']=float(this_week_total_quan)
        chart1['summary2']['value']=float(diff_total_quan)
        
        chart2['primary_data']=list(this_week_sale.items())
        chart2['secondary_data']=list(last_week_sale.items())
        chart2['summary1']['value']= float(this_week_total_sale)
        chart2['summary2']['value']= float(diff_total_sale)

        pi_data=[]
        for d in zip(pd_w1.item__sku.unique(),pd_w1.item__name.unique(),this_week_item_percentage):
            pi_data.append(d)
        chart4['data']=pi_data

        item_data=[]
        for d in zip(pd_w1.item__sku.unique(),pd_w1.item__name.unique(),this_week_item_wise_sale,this_week_item_wise_quan,diff_item_wise):
            item_data.append(d)
        chart3['data']=item_data
    
    #delete old charts
    charts = Salescharts.objects.filter(store=store).first()
    if charts:
        charts.delete()
    #generate data
    chart              = Salescharts()
    chart.store        = store
    chart.chart1       = chart1
    chart.chart2       = chart2
    chart.chart3       = chart3
    chart.chart4       = chart4
    chart.chart5       = chart5
    chart.chart6       = chart6
    chart.save()
    
    return True
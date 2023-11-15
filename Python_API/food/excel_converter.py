# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse

# Create your views here.

from django.views import View
import json
import datetime
import ast

import xlwt
from django.http import HttpResponse
from django.contrib.auth.models import User
import cx_Oracle

###################################################################  DB connection and Static Functions

def get_connection_info_group():
    with open("C:\\db_connect_info\\group\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def get_connection_info_food():
    with open("C:\\db_connect_info\\food\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def get_connection_info_accessories():
    with open("C:\\db_connect_info\\accessories\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def get_connection_info_dev():
    with open("C:\\db_connect_info\\dev\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info


def query_db(query, args=(), one=False):
    try:
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        print(db_connection_info)
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        cur_oracle.execute(query, args)
        r = [dict((cur_oracle.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cur_oracle.fetchall()]
        cur_oracle.connection.close()
        return (r[0] if r else None) if one else r
    except:
        pass


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

###########################################################################################   National Target

def national_target(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_start_date = l_dic['start_date']
        l_end_date = l_dic['end_date']
        l_days = l_dic['days']
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur = con.cursor()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="national_target.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('National Target')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        #font_style.font.bold = True

        header = ['National Target Sheet From ' + l_start_date + ' To' + l_end_date + ' (Days-'+l_days + ') ']

        for col_num in range(len(header)):
            ws.write(row_num, col_num, header[col_num], font_style)

        ws.write(1, 0, 'DP->', font_style)
        ws.write(2, 0, 'TP->', font_style)
        ws.write(3, 0, 'SKU CODE->', font_style)
        ws.write(4, 0, 'SKU QTY->', font_style)
        ws.write(5, 0, 'DP VALUE->', font_style)
        ws.write(6, 0, 'TP VALUE->', font_style)
        ws.write(7, 0, 'DP VALUE WITH 6%->', font_style)

        columns = []


        oracle_sql_1 =   '''select distinct mrti.item_code,
                                   mrti.target_quantity,
                                   mrti.target_amount,
                                   mrti.target_quantity * mrti.ims_rate ims_target,
                                   mrti.target_amount * 106 / 100 dp_106
                            from mkt_national_target mrt,
                                 mkt_national_target_itm mrti
                            where mrt.national_target_id = mrti.national_target_id(+)
                            and mrt.national_target_id in ( select national_target_id from  mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            order by 1'''

        cur.execute(oracle_sql_1, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        items = cur.fetchall()

        oracle_sql_2 =   '''select distinct mrti.item_code,
                                   mrti.target_rate,
                                   mrti.ims_rate
                            from mkt_national_target mrt,
                                 mkt_national_target_itm mrti
                            where mrt.national_target_id = mrti.national_target_id(+)
                            and mrt.national_target_id in (select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            order by 1'''

        cur.execute(oracle_sql_2, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        items_rate = cur.fetchall()

        c=0
        for i in items:
            c = c + 1
            for j in items_rate:
                if i[0] == j[0]:
                    ws.write(1, c, j[1], font_style)
                    ws.write(2, c, j[2], font_style)

        oracle_sql_3 =   '''select SUM(mrti.target_amount) ps_tgt,
                                   SUM(mrti.target_quantity * mrti.ims_rate) ims_target,
                                   SUM(mrti.target_amount * 106 / 100) dp_106
                            from mkt_national_target mrt,
                                 mkt_national_target_itm mrti
                            where mrt.national_target_id = mrti.national_target_id(+)
                            and mrt.national_target_id in ( select national_target_id from  mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            order by 1'''

        cur.execute(oracle_sql_3, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        item_total = cur.fetchall()

        r=3
        c=1
        for i in items:
            ws.write(r, c, i[0], font_style)
            ws.write(r + 1, c, i[1], font_style)
            ws.write(r + 2, c, i[2], font_style)
            ws.write(r + 3, c, i[3], font_style)
            ws.write(r + 4, c, i[4], font_style)
            c = c + 1

        for j in item_total:
            ws.write(3, c, 'TOTAL', font_style)
            #ws.write(2, c, j[0], font_style)
            ws.write(5, c, j[0], font_style)
            ws.write(6, c, j[1], font_style)
            ws.write(7, c, j[2], font_style)

        wb.save(response)
        return response

###########################################################################################   Zone Target

def zone_target(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_start_date = l_dic['start_date']
        l_end_date = l_dic['end_date']
        l_days = l_dic['days']

        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur = con.cursor()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="zone_target.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Zone Target')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        header = ['Zone Target Sheet From ' + l_start_date + ' To' + l_end_date + ' (Days-'+l_days + ') ']

        for col_num in range(len(header)):
            ws.write(row_num, col_num, header[col_num], font_style)

        ws.write(1, 0, 'DP->', font_style)
        ws.write(2, 0, 'TP->', font_style)

        columns = ['SL', 'ZONE','ZSM']

        oracle_sql_1 =   '''select distinct mrti.item_code
                            from mkt_region_target mrt,
                                 mkt_region_target_itm mrti,
                                 mkt_region_target_days mrtd
                            where mrt.region_target_id = mrti.region_target_id(+)
                            and mrt.region_target_id = mrtd.region_target_id(+)
                            and mrtd.target_date between :p_start_date and :p_end_date
                            order by 1'''

        cur.execute(oracle_sql_1, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        items = cur.fetchall()

        for m in items:
            columns.append(m)

        for col_num in range(len(columns)):
            ws.write(3, col_num, columns[col_num], font_style)

        oracle_sql_2 = '''select distinct mrti.item_code,
                                           mrti.target_rate,
                                           mrti.ims_rate
                                    from mkt_region_target mrt,
                                         mkt_region_target_itm mrti
                                    where mrt.region_target_id = mrti.region_target_id(+)
                                    and mrt.national_target_id in (select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                                    order by 1'''

        cur.execute(oracle_sql_2, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        items_rate = cur.fetchall()
        font_style = xlwt.XFStyle()
        c = 2
        for i in items:
            c = c + 1
            for j in items_rate:
                if i[0] == j[0]:
                    ws.write(1, c, j[1], font_style)
                    ws.write(2, c, j[2], font_style)

        oracle_sql_3 =   '''select rownum,
                                   zone_name,
                                   zsm_name
                            from (
                                select distinct mrt.zone_name, 
                                       z.employee_name zsm_name
                                from mkt_region_target mrt,
                                     mkt_region_target_itm mrti,
                                     mkt_region_target_days mrtd,
                                     geo_sales_rsm gr,
                                     hrm_employee_detail z
                                where mrt.region_target_id = mrti.region_target_id(+)
                                and mrt.region_target_id = mrtd.region_target_id(+)
                                and mrt.market_id = gr.region_id(+)
                                and gr.zsm_emp_id = z.employee_id(+)
                                and mrtd.target_date between :p_start_date and :p_end_date
                                order by zone_name
                            )'''

        cur.execute(oracle_sql_3, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        zones = cur.fetchall()
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        row_num = 3
        for zone in zones:
            row_num = row_num + 1
            for col_num in range(len(zone)):
                ws.write(row_num, col_num, zone[col_num],font_style)

        oracle_sql_4 =   '''select distinct zone_name,
                                   item_code,
                                   sum(target_quantity) target_quantity
                            from mkt_region_target mrt,
                                 mkt_region_target_itm mrti
                            where mrt.region_target_id = mrti.region_target_id(+)
                            and mrt.national_target_id in ( select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            group by zone_name,item_code
                            order by 1'''

        cur.execute(oracle_sql_4, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        zone_itme_qty = cur.fetchall()
        l_item_wise_qty_sum = 0
        l_last_row = 0
        r = 3
        c = 2
        for i in items:
            c = c + 1
            for j in zones:
                r = r + 1
                for k in zone_itme_qty:
                    if i[0] == k[1]:
                        if j[1] == k[0]:
                            ws.write(r, c, k[2] ,font_style)
                            l_item_wise_qty_sum = l_item_wise_qty_sum + k[2]
            l_last_row = r
            ws.write(r + 1, c, l_item_wise_qty_sum, font_style)
            r = 3

        ws.write(l_last_row + 1, 0, 'TOTAL SKU', font_style)
        ws.write(l_last_row + 2, 0, 'TOTAL VALUE IN DP', font_style)
        ws.write(l_last_row + 3, 0, 'TOTAL VALUE IN TP', font_style)
        ws.write(l_last_row + 4, 0, 'DP WITH 6%', font_style)

        l_last_column = 0
        c = 2
        for i in items_rate:
            c = c + 1
            l_item_dp_value = 0
            l_item_tp_value = 0
            l_item_106 = 0
            for j in zone_itme_qty:
                r = r + 1
                if i[0] == j[1]:
                    l_item_dp_value = l_item_dp_value + j[2] * i[1]
                    l_item_tp_value = l_item_tp_value + j[2] * i[2]
                    l_item_106 = l_item_dp_value * 106 / 100
            l_last_column = c
            ws.write(l_last_row + 2, c, l_item_dp_value, font_style)
            ws.write(l_last_row + 3, c, l_item_tp_value, font_style)
            ws.write(l_last_row + 4, c, l_item_106, font_style)

        oracle_sql_5 = '''select distinct zone_name,
                               SUM(target_quantity * mrti.target_rate) tgt_value,
                               SUM(target_quantity * mrti.ims_rate) ims_tgt
                        from mkt_region_target mrt,
                             mkt_region_target_itm mrti
                        where mrt.region_target_id = mrti.region_target_id(+)
                        and mrt.national_target_id in (select distinct national_target_id from mkt_region_target_days where target_date between :p_start_date and :p_end_date)
                        group by zone_name
                        order by 1'''

        cur.execute(oracle_sql_5, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        zone_wise_tgt_value = cur.fetchall()
        ws.write(3, l_last_column + 1, 'PS TGT', font_style)
        ws.write(3, l_last_column + 2, 'IMS TGT', font_style)
        r = 3
        for i in zones:
            r = r + 1
            for j in zone_wise_tgt_value:
                if i[1] == j[0]:
                    ws.write(r, l_last_column + 1, j[1], font_style)
                    ws.write(r, l_last_column + 2, j[2], font_style)
        r = 3

        wb.save(response)
        return response

###########################################################################################   Region Target


def region_target(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_start_date = l_dic['start_date']
        l_end_date = l_dic['end_date']
        l_days = l_dic['days']

        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur = con.cursor()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="region_target.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Region Target')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        header = ['Region Wise Target Sheet' + ' ( From: ' + l_start_date + ' To: ' + l_end_date + ' ) ' + ' Days- '+ l_days]

        for col_num in range(len(header)):
            ws.write(row_num, col_num, header[col_num], font_style)

        columns = ['SL', 'ZONE','ZSM','REGION','RSM']

        oracle_sql_2 =   '''select distinct mrti.item_code
                            from mkt_region_target mrt,
                                 mkt_region_target_itm mrti,
                                 mkt_region_target_days mrtd
                            where mrt.region_target_id = mrti.region_target_id(+)
                            and mrt.region_target_id = mrtd.region_target_id(+)
                            and mrtd.target_date between :p_start_date and :p_end_date
                            order by 1'''

        cur.execute(oracle_sql_2, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        items = cur.fetchall()

        for m in items:
            columns.append(m)

        for col_num in range(len(columns)):
            ws.write(3, col_num, columns[col_num], font_style)


        oracle_sql_2 =   '''select distinct mrti.item_code,
                                   mrti.target_rate,
                                   mrti.ims_rate
                            from mkt_region_target mrt,
                                 mkt_region_target_itm mrti
                            where mrt.region_target_id = mrti.region_target_id(+)
                            and mrt.national_target_id in (select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            order by 1'''

        cur.execute(oracle_sql_2, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        items_rate = cur.fetchall()

        ws.write(1, 0, 'DP->', font_style)
        ws.write(2, 0, 'TP->', font_style)

        font_style = xlwt.XFStyle()

        c = 4
        for i in items:
            for j in items_rate:
                if i[0] == j[0]:
                    c = c + 1
                    ws.write(1, c, j[1], font_style)

        c = 4
        for i in items:
            for j in items_rate:
                if i[0] == j[0]:
                    c = c + 1
                    ws.write(2, c, j[2], font_style)

        oracle_sql_3 =   '''select rownum,
                                   zone_name,
                                   zsm_name,
                                   region_name,
                                   rsm_name
                            from (
                                select distinct mrt.zone_name, 
                                       z.employee_name zsm_name,
                                       mrt.region_name,
                                       r.employee_name rsm_name
                                from mkt_region_target mrt,
                                     mkt_region_target_itm mrti,
                                     mkt_region_target_days mrtd,
                                     geo_sales_rsm gr,
                                     hrm_employee_detail r,
                                     hrm_employee_detail z
                                where mrt.region_target_id = mrti.region_target_id(+)
                                and mrt.region_target_id = mrtd.region_target_id(+)
                                and mrt.market_id = gr.region_id(+)
                                and gr.rsm_emp_id = r.employee_id(+)
                                and gr.zsm_emp_id = z.employee_id(+)
                                and mrtd.target_date between :p_start_date and :p_end_date
                                order by zone_name, region_name
                            )'''

        cur.execute(oracle_sql_3, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        regions = cur.fetchall()
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        row_num = 3
        for region in regions:
            row_num = row_num + 1
            for col_num in range(len(region)):
                ws.write(row_num, col_num, region[col_num],font_style)

        oracle_sql_4 =   '''select distinct region_name,
                                   item_code,
                                   SUM(target_quantity) target_quantity 
                            from mkt_region_target mrt,
                                 mkt_region_target_itm mrti
                            where mrt.region_target_id = mrti.region_target_id(+)
                            and mrt.national_target_id in (select distinct national_target_id from mkt_region_target_days where target_date between :p_start_date and :p_end_date)
                            group by region_name, item_code
                            order by 1'''

        cur.execute(oracle_sql_4, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        regions_itmes_qty = cur.fetchall()

        l_item_wise_qty_sum = 0
        l_last_record = 0
        r = 3
        c = 4
        for i in items:
            c = c + 1
            for j in regions:
                r = r + 1
                for k in regions_itmes_qty:
                    if i[0] == k[1]:
                        if j[3] == k[0]:
                            ws.write(r, c, k[2] ,font_style)
                            l_item_wise_qty_sum = l_item_wise_qty_sum + k[2]
            r = r + 1
            l_last_record = r
            ws.write(r, c, l_item_wise_qty_sum, font_style)
            #ws.write(r, 0, 'TOTAL SKU (MKT):', font_style)
            r = 3
            l_item_wise_qty_sum = 0
        ws.write(l_last_record, 0, 'TOTAL SKU (MKT):', font_style)
        ws.write(l_last_record+1, 0, 'TOTAL VALUE IN DP:', font_style)
        ws.write(l_last_record+2, 0, 'TOTAL VALUE IN TP:', font_style)
        ws.write(l_last_record+3, 0, 'DP WITH 6%:', font_style)

        l_last_column = 0
        c = 4
        for i in items_rate:
            c = c + 1
            l_item_dp_value = 0
            l_item_tp_value = 0
            l_item_106 = 0
            for j in regions_itmes_qty:
                r = r + 1
                if i[0] == j[1]:
                    l_item_dp_value = l_item_dp_value + j[2] * i[1]
                    l_item_tp_value = l_item_tp_value + j[2] * i[2]
                    l_item_106 = l_item_dp_value * 106 / 100
            l_last_column = c
            ws.write(l_last_record + 1, c, l_item_dp_value, font_style)
            ws.write(l_last_record + 2, c, l_item_tp_value, font_style)
            ws.write(l_last_record + 3, c, l_item_106, font_style)

        oracle_sql_5 = '''select distinct region_name,
                                   SUM(target_quantity * mrti.target_rate) tgt_value,
                                   SUM(target_quantity * mrti.ims_rate) ims_tgt
                            from mkt_region_target mrt,
                                 mkt_region_target_itm mrti
                            where mrt.region_target_id = mrti.region_target_id(+)
                            and mrt.national_target_id in (select distinct national_target_id from mkt_region_target_days where target_date between :p_start_date and :p_end_date)
                            group by region_name
                            order by 1'''

        cur.execute(oracle_sql_5, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        regions_wise_tgt_value = cur.fetchall()
        ws.write(3, l_last_column + 1, 'PS TGT', font_style)
        ws.write(3, l_last_column + 2, 'IMS TGT', font_style)
        r=3
        for i in regions:
            r = r + 1
            for j in regions_wise_tgt_value:
                if i[3] == j[0]:
                    ws.write(r, l_last_column + 1 , j[1] , font_style)
                    ws.write(r, l_last_column + 2 , j[2], font_style)
        r = 3
        wb.save(response)
        cur.close()
        return response

###########################################################################################   Area Target

def area_target(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_start_date = l_dic['start_date']
        l_end_date = l_dic['end_date']
        l_days = l_dic['days']

        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur = con.cursor()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="area_target.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Area Target')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        header = ['Area Wise Target Sheet' + ' ( From: ' + l_start_date + ' To: ' + l_end_date + ' ) ' + ' Days- '+ str(l_days)]

        for col_num in range(len(header)):
            ws.write(row_num, col_num, header[col_num], font_style)

        ws.write(1, 0, 'DP->', font_style)
        ws.write(2, 0, 'TP->', font_style)

        columns = ['SL', 'ZONE','ZSM','REGION','RSM','AREA','ASM']

        oracle_sql_1 =   '''select distinct mrti.item_code
                            from mkt_territory_target mrt,
                                 mkt_territory_target_itm mrti,
                                 mkt_territory_target_days mrtd
                            where mrt.territory_target_id = mrti.territory_target_id(+)
                            and mrt.territory_target_id = mrtd.territory_target_id(+)
                            and mrtd.target_date between :p_start_date and :p_end_date
                            order by 1'''

        cur.execute(oracle_sql_1, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        items = cur.fetchall()

        for m in items:
            columns.append(m)

        for col_num in range(len(columns)):
            ws.write(3, col_num, columns[col_num], font_style)

        oracle_sql_2 = '''select distinct mrti.item_code,
                                           mrti.target_rate,
                                           mrti.ims_rate
                                    from mkt_territory_target mrt,
                                         mkt_territory_target_itm mrti
                                    where mrt.territory_target_id = mrti.territory_target_id(+)
                                    and mrt.national_target_id in (select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                                    order by 1'''

        cur.execute(oracle_sql_2, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        items_rate = cur.fetchall()

        font_style = xlwt.XFStyle()

        c = 6
        for i in items:
            for j in items_rate:
                if i[0] == j[0]:
                    c = c + 1
                    ws.write(1, c, j[1], font_style)
                    ws.write(2, c, j[2], font_style)

        oracle_sql_3 =   '''select rownum,
                                   zone_name,
                                   zsm_name,
                                   region_name,
                                   rsm_name,
                                   area_name,
                                   asm_name
                            from (
                                select distinct mrt.zone_name, 
                                       z.employee_name zsm_name,
                                       mrt.region_name,
                                       r.employee_name rsm_name,
                                       mrt.area_name,
                                       a.employee_name asm_name
                                from mkt_territory_target mrt,
                                     mkt_territory_target_itm mrti,
                                     mkt_territory_target_days mrtd,
                                     geo_sales_spo gr,
                                     hrm_employee_detail r,
                                     hrm_employee_detail z,
                                     hrm_employee_detail a
                                where mrt.territory_target_id = mrti.territory_target_id(+)
                                and mrt.territory_target_id = mrtd.territory_target_id(+)
                                and mrt.market_id = gr.territory_id(+)
                                and gr.asm_emp_id = a.employee_id(+)
                                and gr.rsm_emp_id = r.employee_id(+)
                                and gr.zsm_emp_id = z.employee_id(+)
                                and mrtd.target_date between :p_start_date and :p_end_date
                                order by zone_name, region_name, area_name
                            )'''

        cur.execute(oracle_sql_3, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        areas = cur.fetchall()
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        row_num = 3
        for area in areas:
            row_num = row_num + 1
            for col_num in range(len(area)):
                ws.write(row_num, col_num, area[col_num],font_style)

        oracle_sql_4 =   '''select distinct area_name,
                                   item_code,
                                   sum(target_quantity) target_quantity
                            from mkt_territory_target mrt,
                                 mkt_territory_target_itm mrti
                            where mrt.territory_target_id = mrti.territory_target_id(+)
                            and mrt.national_target_id in (select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            group by area_name, item_code
                            order by 1'''

        cur.execute(oracle_sql_4, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        areas_itmes_qty = cur.fetchall()

        l_item_wise_qty_sum = 0
        r = 3
        c = 6
        l_last_record = 0
        for i in items:
            c = c + 1
            for j in areas:
                r = r + 1
                for k in areas_itmes_qty:
                    if i[0] == k[1]:
                        if j[5] == k[0]:
                            ws.write(r, c, k[2] ,font_style)
                            l_item_wise_qty_sum = l_item_wise_qty_sum + k[2]
            l_last_record = r
            ws.write(r+1, c, l_item_wise_qty_sum, font_style)
            r = 3

        ws.write(l_last_record + 1, 0, 'TOTAL SKU (MKT):', font_style)
        ws.write(l_last_record + 2, 0, 'TOTAL VALUE IN DP:', font_style)
        ws.write(l_last_record + 3, 0, 'TOTAL VALUE IN TP:', font_style)
        ws.write(l_last_record + 4, 0, 'DP WITH 6%:', font_style)

        l_last_column = 0
        c = 6
        for i in items_rate:
            c = c + 1
            l_item_dp_value = 0
            l_item_tp_value = 0
            l_item_106 = 0
            for j in areas_itmes_qty:
                r = r + 1
                if i[0] == j[1]:
                    l_item_dp_value = l_item_dp_value + j[2] * i[1]
                    l_item_tp_value = l_item_tp_value + j[2] * i[2]
                    l_item_106 = l_item_dp_value * 106 / 100
            l_last_column = c
            ws.write(l_last_record + 2, c, l_item_dp_value, font_style)
            ws.write(l_last_record + 3, c, l_item_tp_value, font_style)
            ws.write(l_last_record + 4, c, l_item_106, font_style)

        oracle_sql_5 = '''select distinct  area_name,
                                           SUM(target_quantity * mrti.target_rate) tgt_value,
                                           SUM(target_quantity * mrti.ims_rate) ims_tgt
                                    from mkt_territory_target mrt,
                                         mkt_territory_target_itm mrti
                                    where mrt.territory_target_id = mrti.territory_target_id(+)
                                    and mrt.national_target_id in (select distinct national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                                    group by area_name
                                    order by 1'''

        cur.execute(oracle_sql_5, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        regions_wise_tgt_value = cur.fetchall()
        ws.write(3, l_last_column + 1, 'PS TGT', font_style)
        ws.write(3, l_last_column + 2, 'IMS TGT', font_style)
        r = 3
        for i in areas:
            r = r + 1
            for j in regions_wise_tgt_value:
                if i[5] == j[0]:
                    ws.write(r, l_last_column + 1, j[1], font_style)
                    ws.write(r, l_last_column + 2, j[2], font_style)
        r = 3

        wb.save(response)
        return response

###########################################################################################   Territory Target

def territory_target(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_start_date = l_dic['start_date']
        l_end_date = l_dic['end_date']
        l_days = l_dic['days']

        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur = con.cursor()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="territory_target.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Territory Target')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        header = ['Territory Wise Target Sheet' + ' ( From: ' + str(l_start_date) + ' To: ' + str(l_end_date) + ' ) ' + ' Days- '+ str(l_days)]

        ws.write(0, 0, header, font_style)

        ws.write(1, 0, 'DP->', font_style)
        ws.write(2, 0, 'TP->', font_style)

        columns = ['SL', 'ZONE','ZSM','REGION','RSM','AREA','ASM','TERRITORY','SPO']

        oracle_sql_1 =   '''select distinct mrti.item_code
                            from mkt_territory_target mrt,
                                 mkt_territory_target_itm mrti,
                                 mkt_territory_target_days mrtd
                            where mrt.territory_target_id = mrti.territory_target_id(+)
                            and mrt.territory_target_id = mrtd.territory_target_id(+)
                            and mrtd.target_date between :p_start_date and :p_end_date
                            order by 1'''

        cur.execute(oracle_sql_1, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        items = cur.fetchall()

        for m in items:
            columns.append(m)
        r=3
        c=1
        for col_num in range(len(columns)):
            ws.write(3, col_num, columns[col_num], font_style)

        oracle_sql_2 = '''select distinct mrti.item_code,
                                   mrti.target_rate,
                                   mrti.ims_rate
                            from mkt_territory_target mrt,
                                 mkt_territory_target_itm mrti
                            where mrt.territory_target_id = mrti.territory_target_id(+)
                            and mrt.national_target_id in (select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            order by 1'''

        cur.execute(oracle_sql_2, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        items_rate = cur.fetchall()

        font_style = xlwt.XFStyle()

        c = 8
        for i in items:
            for j in items_rate:
                if i[0] == j[0]:
                    c = c + 1
                    ws.write(1, c, j[1], font_style)
                    ws.write(2, c, j[2], font_style)

        oracle_sql_3 =   '''select rownum,
                                   zone_name,
                                   zsm_name,
                                   region_name,
                                   rsm_name,
                                   area_name,
                                   asm_name,
                                   territory_name,
                                   spo_name
                            from (
                                select distinct mrt.zone_name, 
                                       z.employee_name zsm_name,
                                       mrt.region_name,
                                       r.employee_name rsm_name,
                                       mrt.area_name,
                                       a.employee_name asm_name,
                                       mrt.territory_name,
                                       s.employee_name spo_name 
                                from mkt_territory_target mrt,
                                     mkt_territory_target_itm mrti,
                                     mkt_territory_target_days mrtd,
                                     geo_sales_spo gr,
                                     hrm_employee_detail r,
                                     hrm_employee_detail z,
                                     hrm_employee_detail a,
                                     hrm_employee_detail s
                                where mrt.territory_target_id = mrti.territory_target_id(+)
                                and mrt.territory_target_id = mrtd.territory_target_id(+)
                                and mrt.market_id = gr.territory_id(+)
                                and gr.spo_emp_id = s.employee_id(+)
                                and gr.asm_emp_id = a.employee_id(+)
                                and gr.rsm_emp_id = r.employee_id(+)
                                and gr.zsm_emp_id = z.employee_id(+)
                                and mrtd.target_date between :p_start_date and :p_end_date
                                order by zone_name, region_name, area_name, territory_name
                            )'''

        cur.execute(oracle_sql_3, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        territories = cur.fetchall()
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        row_num = 3
        c = 0
        for i in territories:
            row_num = row_num + 1
            ws.write(row_num, 0, i[0], font_style)
            ws.write(row_num, 1, i[1], font_style)
            ws.write(row_num, 2, i[2], font_style)
            ws.write(row_num, 3, i[3], font_style)
            ws.write(row_num, 4, i[4], font_style)
            ws.write(row_num, 5, i[5], font_style)
            ws.write(row_num, 6, i[6], font_style)
            ws.write(row_num, 7, i[7], font_style)
            ws.write(row_num, 8, i[8], font_style)

        #    print(i)
            #ws.write(row_num, c, i[2], font_style)
            #for col_num in range(len(territory)):
                #ws.write(row_num, col_num, territory[col_num],font_style)

        oracle_sql_4 =   '''select distinct territory_name,
                                   item_code,
                                   sum(nvl(target_quantity,0)) target_quantity
                            from mkt_territory_target mrt,
                                 mkt_territory_target_itm mrti
                            where mrt.territory_target_id = mrti.territory_target_id(+)
                            and mrt.national_target_id in (select national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            group by territory_name, item_code
                            order by 1'''

        cur.execute(oracle_sql_4, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        territories_itmes_qty = cur.fetchall()

        r = 3
        c = 8
        l_item_wise_qty_sum = 0
        l_last_record = 0
        for i in items:
            c = c + 1
            for j in territories:
                r = r + 1
                for k in territories_itmes_qty:
                    if i[0] == k[1]:
                        if j[7] == k[0]:
                            ws.write(r, c, k[2] ,font_style)
                            l_item_wise_qty_sum = l_item_wise_qty_sum + k[2]
            l_last_record = r
            ws.write(r + 1, c, l_item_wise_qty_sum, font_style)
            r = 3

        ws.write(l_last_record + 1, 0, 'TOTAL SKU (MKT):', font_style)
        ws.write(l_last_record + 2, 0, 'TOTAL VALUE IN DP:', font_style)
        ws.write(l_last_record + 3, 0, 'TOTAL VALUE IN TP:', font_style)
        ws.write(l_last_record + 4, 0, 'DP WITH 6%:', font_style)

        l_last_column = 0
        c = 8
        for i in items_rate:
            c = c + 1
            l_item_dp_value = 0
            l_item_tp_value = 0
            l_item_106 = 0
            for j in territories_itmes_qty:
                r = r + 1
                if i[0] == j[1]:
                    l_item_dp_value = l_item_dp_value + j[2] * i[1]
                    l_item_tp_value = l_item_tp_value + j[2] * i[2]
                    l_item_106 = l_item_dp_value * 106 / 100
            l_last_column = c
            ws.write(l_last_record + 2, c, l_item_dp_value, font_style)
            ws.write(l_last_record + 3, c, l_item_tp_value, font_style)
            ws.write(l_last_record + 4, c, l_item_106, font_style)

        oracle_sql_5 = '''select distinct  territory_name,
                                   SUM(target_quantity * mrti.target_rate) tgt_value,
                                   SUM(target_quantity * mrti.ims_rate) ims_tgt
                            from mkt_territory_target mrt,
                                 mkt_territory_target_itm mrti
                            where mrt.territory_target_id = mrti.territory_target_id(+)
                            and mrt.national_target_id in (select distinct national_target_id from mkt_national_target_days where target_date between :p_start_date and :p_end_date)
                            group by territory_name
                            order by 1'''

        cur.execute(oracle_sql_5, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        territory_wise_tgt_value = cur.fetchall()
        ws.write(3, l_last_column + 1, 'PS TGT', font_style)
        ws.write(3, l_last_column + 2, 'IMS TGT', font_style)
        r = 3
        for i in territories:
            r = r + 1
            for j in territory_wise_tgt_value:
                if i[7] == j[0]:
                    ws.write(r, l_last_column + 1, j[1], font_style)
                    ws.write(r, l_last_column + 2, j[2], font_style)
        r = 3
        wb.save(response)
        return response

############################################################################################## ims report sku qty wise

def sku_qty_wise_ims(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_start_date = l_dic['start_date']
        l_end_date = l_dic['end_date']
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur = con.cursor()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="sku_qty_wise_ims.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('SKU QTY WISE IMS')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        #font_style.font.bold = True


        header = ['SKU Qty wise IMS From ' + l_start_date + ' To' + l_end_date]
        ws.write(0, 0, header, font_style)

        columns = ['SL', 'ZONE', 'ZONE ID', 'ZSM', 'ZSM ID', 'REGION', 'REGION ID' ,'RSM', 'RSM ID' ,'AREA', 'AREA ID' ,'ASM', 'ASM ID' ,'TERRITORY', 'TERRITORY ID' ,'SPO', 'SPO ID']

        oracle_sql_1 =   '''SELECT DISTINCT ipd.item_code
                            FROM ims_process_mst ipm,
                                 ims_process_dtl ipd
                            WHERE ipm.ims_process_mst_id = ipd.ims_process_mst_id
                            AND ipm.is_formatted = 'F'
                            AND ipm.sales_personnel_type = 4
                            AND ipm.delivery_date BETWEEN :p_start_date AND :p_end_date
                            ORDER BY 1'''

        cur.execute(oracle_sql_1, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        items = cur.fetchall()

        for m in items:
            columns.append(m)

        for col_num in range(len(columns)):
            ws.write(1, col_num, columns[col_num], font_style)

        oracle_sql_2 =   '''WITH ipm AS (SELECT spo_id,
                                                 asm_id,
                                                 rsm_id,
                                                 zsm_id,
                                                 territory_id,
                                                 area_id,
                                                 region_id,
                                                 zone_id,
                                                 distributor_id,
                                                 upper_id
                                            FROM ims_process_mst ipm
                                           WHERE is_formatted = 'F'
                                                 AND sales_personnel_type = 4
                                                 AND delivery_date BETWEEN :p_start_date AND :p_end_date
                                        GROUP BY spo_id,
                                                 asm_id,
                                                 rsm_id,
                                                 zsm_id,
                                                 territory_id,
                                                 area_id,
                                                 region_id,
                                                 zone_id,
                                                 distributor_id,
                                                 upper_id
                                        ORDER BY spo_id)
                                 SELECT DISTINCT gz.zone_name,
                                        ipm.zone_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 zsm.first_name
                                              || ' '
                                              || zsm.middle_name
                                              || ' '
                                              || zsm.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           zsm_name,
                                        zsm.employee_id zsm_emp_id,
                                        gr.region_name,
                                        ipm.region_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 rsm.first_name
                                              || ' '
                                              || rsm.middle_name
                                              || ' '
                                              || rsm.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           rsm_name,
                                        rsm.employee_id rsm_emp_id,
                                        ga.area_name,
                                        ipm.area_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 asm.first_name
                                              || ' '
                                              || asm.middle_name
                                              || ' '
                                              || asm.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           asm_name,
                                        asm.employee_id asm_emp_id,
                                        gt.territory_name,
                                        ipm.territory_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 spo.first_name
                                              || ' '
                                              || spo.middle_name
                                              || ' '
                                              || spo.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           spo_name,
                                        spo.employee_id spo_emp_id,
                                        ipm.distributor_id,
                                        ipm.upper_id
                                   FROM ipm,
                                        hrm_employee spo,
                                        hrm_employee asm,
                                        hrm_employee rsm,
                                        hrm_employee zsm,
                                        geo_zone gz,
                                        geo_region gr,
                                        geo_area ga,
                                        geo_territory gt
                                  WHERE ipm.spo_id = spo.employee_id(+)
                                        AND ipm.asm_id = asm.employee_id(+)
                                        AND ipm.rsm_id = rsm.employee_id(+)
                                        AND ipm.zsm_id = zsm.employee_id(+)
                                        AND ipm.territory_id = gt.territory_id(+)
                                        AND ipm.area_id = ga.area_id(+)
                                        AND ipm.region_id = gr.region_id(+)
                                        AND ipm.zone_id = gz.zone_id(+)
                                ORDER BY zone_name,
                                        region_name,
                                        area_name,
                                        territory_name,
                                        spo_name'''

        cur.execute(oracle_sql_2, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        spo = cur.fetchall()
        r = 2
        c = 1
        sl = 1
        for i in spo:
            ws.write(r, 0, sl, font_style)
            ws.write(r, 1, i[0], font_style)
            ws.write(r, 2, i[1], font_style)
            ws.write(r, 3, i[2], font_style)
            ws.write(r, 4, i[3], font_style)
            ws.write(r, 5, i[4], font_style)
            ws.write(r, 6, i[5], font_style)
            ws.write(r, 7, i[6], font_style)
            ws.write(r, 8, i[7], font_style)
            ws.write(r, 9, i[8], font_style)
            ws.write(r, 10, i[9], font_style)
            ws.write(r, 11, i[10], font_style)
            ws.write(r, 12, i[11], font_style)
            ws.write(r, 13, i[12], font_style)
            ws.write(r, 14, i[13], font_style)
            ws.write(r, 15, i[14], font_style)
            ws.write(r, 16, i[15], font_style)
            sl = sl + 1
            r = r + 1

        oracle_sql_3 =   '''SELECT spo_id,
                                 asm_id,
                                 rsm_id,
                                 zsm_id,
                                 territory_id,
                                 area_id,
                                 region_id,
                                 zone_id,
                                 ipd.item_code,
                                 SUM(ipd.item_qty) item_qty,
                                 ipm.distributor_id,
                                 ipm.upper_id
                            FROM ims_process_mst ipm,
                                 (SELECT ims_process_mst_id, 
                                         item_code,
                                         SUM(market_qty) item_qty,
                                         SUM(market_qty * market_unit_rate) item_value,
                                         SUM (amount) item_tdv
                                  FROM ims_process_dtl ipd
                                  GROUP BY ims_process_mst_id,
                                           item_code) ipd
                           WHERE     ipm.ims_process_mst_id = ipd.ims_process_mst_id(+)
                                 AND is_formatted = 'F'
                                 AND sales_personnel_type = 4
                                 AND delivery_date BETWEEN :p_start_date AND :p_end_date
                        GROUP BY spo_id,
                                 asm_id,
                                 rsm_id,
                                 zsm_id,
                                 territory_id,
                                 area_id,
                                 region_id,
                                 zone_id,
                                 item_code,
                                 distributor_id,
                                 upper_id
                        ORDER BY spo_id'''

        cur.execute(oracle_sql_3, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        spo_item_qty = cur.fetchall()
        row = 1
        col = 16
        for i in items:
            col = col + 1
            for j in spo:
                row = row + 1
                for k in spo_item_qty:
                    if i[0] == k[8]:
                        if k[0] == j[15] and k[1] == j[11] and k[2] == j[7] and  k[3] == j[3] and k[4] == j[13] and k[5] == j[9] and k[6] == j[5] and k[7] == j[1] and k[10] == j[16] and k[11] == j[17]:
                            ws.write(row, col, k[9], font_style)
            row = 1

        wb.save(response)
        return response


############################################################################################## ims report sku value wise

def sku_value_wise_ims(request):
    if request.method == 'GET':
        l_data = request.GET
        l_dic = l_data.dict()
        l_start_date = l_dic['start_date']
        l_end_date = l_dic['end_date']
        list_conn_info = get_connection_info_food()
        db_connection_info = str(list_conn_info[0])
        con = cx_Oracle.connect(db_connection_info)
        cur = con.cursor()

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="sku_value_wise_ims.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('SKU VALUE WISE IMS')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        #font_style.font.bold = True


        header = ['SKU Qty wise IMS From ' + l_start_date + ' To' + l_end_date]
        ws.write(0, 0, header, font_style)

        columns = ['SL', 'ZONE', 'ZONE ID', 'ZSM', 'ZSM ID', 'REGION', 'REGION ID' ,'RSM', 'RSM ID' ,'AREA', 'AREA ID' ,'ASM', 'ASM ID' ,'TERRITORY', 'TERRITORY ID' ,'SPO', 'SPO ID']

        oracle_sql_1 =   '''SELECT DISTINCT ipd.item_code
                            FROM ims_process_mst ipm,
                                 ims_process_dtl ipd
                            WHERE ipm.ims_process_mst_id = ipd.ims_process_mst_id
                            AND ipm.is_formatted = 'F'
                            AND ipm.sales_personnel_type = 4
                            AND ipm.delivery_date BETWEEN :p_start_date AND :p_end_date
                            ORDER BY 1'''

        cur.execute(oracle_sql_1, {'p_start_date':l_start_date, 'p_end_date':l_end_date})

        items = cur.fetchall()

        for m in items:
            columns.append(m)

        for col_num in range(len(columns)):
            ws.write(1, col_num, columns[col_num], font_style)

        oracle_sql_2 =   '''WITH ipm AS (SELECT spo_id,
                                                 asm_id,
                                                 rsm_id,
                                                 zsm_id,
                                                 territory_id,
                                                 area_id,
                                                 region_id,
                                                 zone_id,
                                                 distributor_id,
                                                 upper_id
                                            FROM ims_process_mst ipm
                                           WHERE is_formatted = 'F'
                                                 AND sales_personnel_type = 4
                                                 AND delivery_date BETWEEN :p_start_date AND :p_end_date
                                        GROUP BY spo_id,
                                                 asm_id,
                                                 rsm_id,
                                                 zsm_id,
                                                 territory_id,
                                                 area_id,
                                                 region_id,
                                                 zone_id,
                                                 distributor_id,
                                                 upper_id
                                        ORDER BY spo_id)
                                 SELECT DISTINCT gz.zone_name,
                                        ipm.zone_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 zsm.first_name
                                              || ' '
                                              || zsm.middle_name
                                              || ' '
                                              || zsm.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           zsm_name,
                                        zsm.employee_id zsm_emp_id,
                                        gr.region_name,
                                        ipm.region_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 rsm.first_name
                                              || ' '
                                              || rsm.middle_name
                                              || ' '
                                              || rsm.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           rsm_name,
                                        rsm.employee_id rsm_emp_id,
                                        ga.area_name,
                                        ipm.area_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 asm.first_name
                                              || ' '
                                              || asm.middle_name
                                              || ' '
                                              || asm.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           asm_name,
                                        asm.employee_id asm_emp_id,
                                        gt.territory_name,
                                        ipm.territory_id,
                                        REGEXP_REPLACE (
                                           TRIM (
                                                 spo.first_name
                                              || ' '
                                              || spo.middle_name
                                              || ' '
                                              || spo.last_name
                                              || ' '),
                                           '[[:space:]]+',
                                           ' ')
                                           spo_name,
                                        spo.employee_id spo_emp_id,
                                        ipm.distributor_id,
                                        ipm.upper_id
                                   FROM ipm,
                                        hrm_employee spo,
                                        hrm_employee asm,
                                        hrm_employee rsm,
                                        hrm_employee zsm,
                                        geo_zone gz,
                                        geo_region gr,
                                        geo_area ga,
                                        geo_territory gt
                                  WHERE ipm.spo_id = spo.employee_id(+)
                                        AND ipm.asm_id = asm.employee_id(+)
                                        AND ipm.rsm_id = rsm.employee_id(+)
                                        AND ipm.zsm_id = zsm.employee_id(+)
                                        AND ipm.territory_id = gt.territory_id(+)
                                        AND ipm.area_id = ga.area_id(+)
                                        AND ipm.region_id = gr.region_id(+)
                                        AND ipm.zone_id = gz.zone_id(+)
                                ORDER BY zone_name,
                                        region_name,
                                        area_name,
                                        territory_name,
                                        spo_name'''

        cur.execute(oracle_sql_2, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        spo = cur.fetchall()
        r = 2
        c = 1
        sl = 1
        for i in spo:
            ws.write(r, 0, sl, font_style)
            ws.write(r, 1, i[0], font_style)
            ws.write(r, 2, i[1], font_style)
            ws.write(r, 3, i[2], font_style)
            ws.write(r, 4, i[3], font_style)
            ws.write(r, 5, i[4], font_style)
            ws.write(r, 6, i[5], font_style)
            ws.write(r, 7, i[6], font_style)
            ws.write(r, 8, i[7], font_style)
            ws.write(r, 9, i[8], font_style)
            ws.write(r, 10, i[9], font_style)
            ws.write(r, 11, i[10], font_style)
            ws.write(r, 12, i[11], font_style)
            ws.write(r, 13, i[12], font_style)
            ws.write(r, 14, i[13], font_style)
            ws.write(r, 15, i[14], font_style)
            ws.write(r, 16, i[15], font_style)
            sl = sl + 1
            r = r + 1

        oracle_sql_3 =   '''SELECT spo_id,
                                 asm_id,
                                 rsm_id,
                                 zsm_id,
                                 territory_id,
                                 area_id,
                                 region_id,
                                 zone_id,
                                 ipd.item_code,
                                 SUM(ipd.item_value) item_value,
                                 ipm.distributor_id,
                                 ipm.upper_id
                            FROM ims_process_mst ipm,
                                 (SELECT ims_process_mst_id, 
                                         item_code,
                                         SUM(market_qty) item_qty,
                                         SUM(market_qty * market_unit_rate) item_value,
                                         SUM (amount) item_tdv
                                  FROM ims_process_dtl ipd
                                  GROUP BY ims_process_mst_id,
                                           item_code) ipd
                           WHERE     ipm.ims_process_mst_id = ipd.ims_process_mst_id(+)
                                 AND is_formatted = 'F'
                                 AND sales_personnel_type = 4
                                 AND delivery_date BETWEEN :p_start_date AND :p_end_date
                        GROUP BY spo_id,
                                 asm_id,
                                 rsm_id,
                                 zsm_id,
                                 territory_id,
                                 area_id,
                                 region_id,
                                 zone_id,
                                 item_code,
                                 distributor_id,
                                 upper_id
                        ORDER BY spo_id'''

        cur.execute(oracle_sql_3, {'p_start_date': l_start_date, 'p_end_date': l_end_date})

        spo_item_qty = cur.fetchall()
        row = 1
        col = 16
        for i in items:
            col = col + 1
            for j in spo:
                row = row + 1
                for k in spo_item_qty:
                    if i[0] == k[8]:
                        if k[0] == j[15] and k[1] == j[11] and k[2] == j[7] and  k[3] == j[3] and k[4] == j[13] and k[5] == j[9] and k[6] == j[5] and k[7] == j[1] and k[10] == j[16] and k[11] == j[17]:
                            ws.write(row, col, k[9], font_style)
            row = 1

        wb.save(response)
        return response
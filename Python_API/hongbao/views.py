# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse

# Create your views here.

import cx_Oracle
import json
import datetime
from django.views import View

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

def get_connection_info_hongbao():
    with open("C:\\db_connect_info\\hongbao\\db_connection.txt") as f:
        conn_info = f.readlines()
    conn_info = [x.strip() for x in conn_info]
    return conn_info

def query_db(query, args=(), one=False):
    try:
        list_conn_info = get_connection_info_hongbao()
        db_connection_info = str(list_conn_info[0])
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


#################################################################################################################

def customer_paid_bill(request):
    if request.method == 'GET':
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_sales_id = l_dic["sales_id"]
        oracle_sql = '''SELECT a.memo_no,
                               a.card_no,
                               b.item_id,
                               c.item_name,
                               c.rate,
                               b.qty,
                               (c.rate * b.qty) total,
                               a.discount_per,
                               a.discount*-1 discount,
                               a.collection_amount,
                               to_char(a.sales_date, 'dd/mm/rrrr') sales_date,
                               to_char(a.sales_date,'hh:mi:ss AM') sales_time,
                               h.name served_by,
                               a.vat_amount,
                               a.pay_amount,
                               a.change_amount,
                               a.service_charge,
                               rt.table_name
                          FROM inv_sales_mst a, 
                               inv_sales_dtl b, 
                               inv_items c,
                               hr_employees h,
                               res_table rt
                         WHERE a.id = b.sales_mst_id(+)
                         AND b.item_id = c.id(+)
                         AND a.waiter_id = h.id(+)
                         AND a.table_id = rt.table_id(+)
                         AND b.item_id is not null
                         AND a.id = :p_sales_id'''
        my_query = query_db(oracle_sql, {'p_sales_id': l_sales_id})
        l_json_output = json.dumps(my_query, default=myconverter)
        return HttpResponse(l_json_output)


class kitchen_order_taking(View):
    def get(self, request):
        if request.method == 'GET':
            print(request.GET)
            l_data = request.GET
            l_dic = l_data.dict()
            l_sales_id = l_dic["sales_id"]
            oracle_sql = '''SELECT a.memo_no,
                                   a.card_no,
                                   b.item_id,
                                   c.item_name,
                                   c.rate,
                                   b.qty,
                                   (c.rate * b.qty) total,
                                   a.discount_per,
                                   a.discount*-1 discount,
                                   a.collection_amount,
                                   to_char(a.sales_date, 'dd/mm/rrrr') sales_date,
                                   to_char(a.sales_date,'hh:mi:ss AM') sales_time,
                                   h.name served_by,
                                   a.vat_amount,
                                   a.pay_amount,
                                   a.change_amount,
                                   rt.table_name,
                                   c.printer_no,
                                   b.hold_fire,
                                   b.remarks
                              FROM inv_sales_mst a, 
                                   inv_sales_dtl b, 
                                   inv_items c,
                                   hr_employees h,
                                   res_table rt
                             WHERE a.id = b.sales_mst_id(+)
                             AND b.item_id = c.id(+)
                             AND a.waiter_id = h.id(+)
                             AND a.table_id = rt.table_id(+)
                             AND b.item_id is not null
                             AND a.id = :p_sales_id'''
            my_query = query_db(oracle_sql, {'p_sales_id': l_sales_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)
            
class kot_fire(View):
    def get(self, request):
        if request.method == 'GET':
            print(request.GET)
            l_data = request.GET
            l_dic = l_data.dict()
            l_sales_dtl_id = l_dic["sales_dtl_id"]
            oracle_sql = '''SELECT a.memo_no,
                               a.card_no,
                               b.item_id,
                               c.item_name,
                               c.rate,
                               b.qty,
                               (c.rate * b.qty) total,
                               a.discount_per,
                               a.discount*-1 discount,
                               a.collection_amount,
                               to_char(a.sales_date, 'dd/mm/rrrr') sales_date,
                               to_char(a.sales_date,'hh:mi:ss AM') sales_time,
                               h.name served_by,
                               a.vat_amount,
                               a.pay_amount,
                               a.change_amount,
                               rt.table_name,
                               c.printer_no,
                               b.hold_fire,
                               b.remarks
                          FROM inv_sales_mst a, 
                               inv_sales_dtl b, 
                               inv_items c,
                               hr_employees h,
                               res_table rt
                         WHERE a.id = b.sales_mst_id(+)
                         AND b.item_id = c.id(+)
                         AND a.waiter_id = h.id(+)
                         AND a.table_id = rt.table_id(+)
                         AND b.item_id is not null
                         AND b.id = :p_sales_dtl_id'''
            my_query = query_db(oracle_sql, {'p_sales_dtl_id': l_sales_dtl_id})
            l_json_output = json.dumps(my_query, default=myconverter)
            return HttpResponse(l_json_output)
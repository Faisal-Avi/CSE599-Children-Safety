from django.views import View
from django.shortcuts import render, HttpResponse
import cx_Oracle
import json, ast
import datetime

db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'

def query_units(request):
	if request.method == 'GET':
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		oracle_sql = '''SELECT pid unit_id,
							   short_name unit_name
						FROM unit@dblink_food'''
		my_query = query_db(oracle_sql)
		l_json_output = json.dumps(my_query)
		return HttpResponse(l_json_output)


def ins_outlet_order_mst(request):
	if request.method == 'GET':
		db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'		
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		l_data = request.GET
		l_dic = l_data.dict()
		l_order_date = l_dic['order_date']
		l_outlet_id = l_dic['outlet_id']
		l_route_id = l_dic['route_id']
		l_distributor_id = l_dic['distributor_id']
		l_created_by = l_dic['created_by']
		l_created_dttm = l_dic['created_dttm']
		l_out_order_id = cur_oracle.var(int)
		l_out_order_no = cur_oracle.var(str)
		cur_oracle.callproc("front_end_support_tool.ins_outlet_order_mst",
							[l_order_date, l_outlet_id, l_route_id, l_distributor_id, l_created_by, l_created_dttm, l_out_order_id,l_out_order_no])
		con.commit()
		con.close()
		l_authentication_result = {"order_id": l_out_order_id.getvalue(), "order_no": l_out_order_no.getvalue()}
		l_json_output = json.dumps(l_authentication_result)
		return HttpResponse(l_json_output)
			
def upd_outlet_order_mst(request):
	if request.method == 'GET':
		db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		l_data = request.GET
		l_dic = l_data.dict()
		l_order_id = l_dic['order_id']
		l_order_date = l_dic['order_date']
		l_outlet_id = l_dic['outlet_id']
		l_route_id = l_dic['route_id']
		l_distributor_id = l_dic['distributor_id']
		l_update_by = l_dic['updated_by']
		l_updated_dttm = l_dic['updated_dttm']
		cur_oracle.callproc("front_end_support_tool.upd_outlet_order_mst",
							[l_order_id,l_order_date,l_outlet_id,l_route_id,l_distributor_id,l_update_by,l_updated_dttm])
		con.commit()
		con.close()
		return HttpResponse(True)
def ins_outlet_order_dtl(request):
	if request.method == 'GET':
		db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		l_data = request.GET
		l_dic = l_data.dict()
		l_master_id = l_dic['order_id']
		l_item_id = l_dic['item_id']
		l_qty = l_dic['qty']
		l_unit_id = l_dic['unit_id']
		l_rate = l_dic['rate']
		l_amount = l_dic['amount']
		l_status = l_dic['status']
		l_created_by = l_dic['created_by']
		l_created_dttm = l_dic['created_dttm']
		cur_oracle.callproc("front_end_support_tool.ins_outlet_order_dtl",
							[l_master_id, l_item_id, l_qty, l_unit_id, l_rate, l_amount, l_status,l_created_by,l_created_dttm])
		con.commit()
		con.close()
		return HttpResponse(True)

def upd_outlet_order_dtl(request):
	if request.method == 'GET':
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		l_data = request.GET
		l_dic = l_data.dict()
		l_dtl_id = l_dic['order_detail_id']
		l_item_id = l_dic['item_id']
		l_qty = l_dic['qty']
		l_unit_id = l_dic['unit_id']
		l_rate = l_dic['rate']
		l_amount = l_dic['amount']
		l_status = l_dic['status']
		l_updated_by = l_dic['updated_by']
		l_updated_dttm = l_dic['updated_dttm']
		cur_oracle.callproc("front_end_support_tool.upd_outlet_order_dtl",
							[l_dtl_id,l_item_id,l_qty,l_unit_id,l_rate,l_amount,l_status,l_updated_by,l_updated_dttm])
		con.commit()
		con.close()
		return HttpResponse(True)

def del_outlet_order_dtl(request):
	if request.method == 'GET':
		db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'		
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		l_data = request.GET
		l_dic = l_data.dict()
		l_order_detail_id = l_dic['order_detail_id']
		cur_oracle.callproc("front_end_support_tool.del_outlet_order_dtl",
							[l_order_detail_id])
		con.commit()
		con.close()
		return HttpResponse(True)

def del_outlet_order(request):
	if request.method == 'GET':
		db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		l_data = request.GET
		l_dic = l_data.dict()
		l_order_id = l_dic['order_id']
		cur_oracle.callproc("front_end_support_tool.del_outlet_order",
							[l_order_id])
		con.commit()
		con.close()
		return HttpResponse(True)

def food_category_product(request):
	if request.method == 'GET':
		db_connection_info = 'bottomerp/dekkkoerp#sdi#@192.168.66.24/dcoproddb1'
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		print(request.GET)
		l_data = request.GET
		l_dic = l_data.dict()  # queryDict tO Dictionary
		l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
		con.commit()
		con.close()
		oracle_sql = '''WITH t_offer
						AS (
							SELECT t.item_pid trade_item_id,
								   t.trade_qty,
								   iu.short_name trade_unit,
								   t.offer_item offer_item_id,
								   oi.item_name offer_item_name,
								   t.offer_qty,
								   ou.short_name offer_unit
							FROM trade_offer@dblink_food t,
								 item@dblink_food ai,
								 item@dblink_food oi,
								 unit@dblink_food iu,
								 unit@dblink_food ou
							WHERE t.item_pid = ai.pid(+)
							AND t.offer_item = oi.pid(+)
							AND ai.market_unit_pid = iu.pid(+) 
							AND t.unit_pid = ou.pid(+)
							AND SYSDATE BETWEEN t.offer_from AND t.offer_to
						)
						SELECT ig.group_name item_category,
							   i.item_name,
							   i.item_code,
							   i.tp unit_price,
							   u.short_name unit_name,
							   mu.short_name market_unit,
							   i.conversion_value,
							   'http://103.199.108.43/FOOD_PRODUCTS/'||i.pid||'.jpg' image_url,
							   i.pid item_id,
							   TO_CHAR(NVL(t_offer.trade_qty,0)) trade_qty,
							   t_offer.offer_item_id,
							   t_offer.offer_item_name,
							   t_offer.offer_qty,
							   t_offer.offer_unit
						FROM item_group@dblink_food ig,
							 item@dblink_food i,
							 unit@dblink_food u,
							 unit@dblink_food mu,
							 t_offer
						WHERE ig.pid = i.item_group_pid(+)
						AND i.unit_pid = u.pid(+)
						AND i.market_unit_pid = mu.pid(+)
						AND i.pid = t_offer.trade_item_id(+)
						AND i.active_status = 'Y'
						AND ig.group_name NOT IN ('PROMOTIONAL','PRODUCTION','E DRINK','OTHERS')
						ORDER BY 1,2'''
		my_query = query_db(oracle_sql)
		l_json_output = json.dumps(my_query)
		return HttpResponse(l_json_output)

def trade_offer(request):
	if request.method == 'GET':
		db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
		con = cx_Oracle.connect(db_connection_info)
		cur_oracle = con.cursor()
		print(request.GET)
		l_data = request.GET
		l_dic = l_data.dict()  # queryDict tO Dictionary
		l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
		con.commit()
		con.close()
		oracle_sql = '''SELECT t.item_pid trade_item_id,
							   t.trade_qty,
							   iu.short_name trade_unit,
							   t.offer_item offer_item_id,
							   oi.item_name offer_item_name,
							   t.offer_qty,
							   ou.short_name offer_unit
						FROM trade_offer@dblink_food t,
							 item@dblink_food ai,
							 item@dblink_food oi,
							 unit@dblink_food iu,
							 unit@dblink_food ou
						WHERE t.item_pid = ai.pid(+)
						AND t.offer_item = oi.pid(+)
						AND ai.market_unit_pid = iu.pid(+) 
						AND t.unit_pid = ou.pid(+)
						AND SYSDATE BETWEEN t.offer_from AND t.offer_to'''
		my_query = query_db(oracle_sql)
		l_json_output = json.dumps(my_query)
		return HttpResponse(l_json_output)

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def query_outlet_order_mst(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_id = l_dic["order_id"]
        oracle_sql = '''SELECT *
                        FROM outlet_order_mst@dblink_food
                        WHERE id = :order_id'''
        my_query = query_db(oracle_sql, {'order_id': l_order_id})
        l_json_output = json.dumps(my_query, default = myconverter)
        return HttpResponse(l_json_output)

def query_outlet_order_dtl(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_order_id = l_dic["order_id"]
        oracle_sql = '''SELECT *
                        FROM outlet_order_dtl@dblink_food
                        WHERE master_id = :order_id'''
        my_query = query_db(oracle_sql, {'order_id': l_order_id})
        l_json_output = json.dumps(my_query, default = myconverter)
        return HttpResponse(l_json_output)

def query_db(query, args=(), one=False):
    db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
    con = cx_Oracle.connect(db_connection_info)
    cur_oracle = con.cursor()
    cur_oracle.execute(query, args)
    r = [dict((cur_oracle.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur_oracle.fetchall()]
    cur_oracle.connection.close()
    return (r[0] if r else None) if one else r
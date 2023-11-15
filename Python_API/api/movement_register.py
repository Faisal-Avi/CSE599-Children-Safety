from django.shortcuts import render, HttpResponse
import cx_Oracle
import json, ast
import datetime

rows = [(1, "First"),
        (2, "Second")]


def query_db(query, args=(), one=False):
    db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
    con = cx_Oracle.connect(db_connection_info)
    cur_oracle = con.cursor()
    cur_oracle.execute(query, args)
    r = [dict((cur_oracle.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur_oracle.fetchall()]
    cur_oracle.connection.close()
    return (r[0] if r else None) if one else r

def movement_register(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        con.commit()
        con.close()

def ins_movement_register(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  # queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        l_movement_date = l_dic["movement_date"]
        l_out_dttm = l_dic["out_dttm"]
        l_in_dttm = l_dic["in_dttm"]
        l_location_from = l_dic["location_from"]
        l_location_to = l_dic["location_to"]
        l_purpose = l_dic["purpose"]
        cur_oracle.callproc("front_end_support_tool.ins_movement_register",
                  [l_emp_id,l_movement_date,l_out_dttm,l_in_dttm,l_location_from,l_location_to,l_purpose])
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        con.commit()
        con.close()
        return HttpResponse(True)

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def query_movement_register(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_emp_id = l_dic["employee_id"]
        l_reference = l_dic["reference"]
        oracle_sql = '''SELECT movement_id,
                               employee_id,
                               TO_CHAR(movement_date , 'DD-MON-RRRR') movement_date,
                               out_dttm,
                               in_dttm,
                               location_from,
                               location_to,
                               purpose,
                               purpose_type,
                               reference
                        FROM hrm_movement_register
                        WHERE employee_id = :emp_id
                        AND reference = :ref
                     '''
        my_query = query_db(oracle_sql, {'emp_id': l_emp_id,'ref': l_reference})
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def query_movement_register_all(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_movement_date = l_dic["movement_date"]
        oracle_sql = '''SELECT movement_id,
                               employee_id,
                               TO_CHAR(movement_date , 'DD-MON-RRRR') movement_date,
                               out_dttm,
                               in_dttm,
                               location_from,
                               location_to,
                               purpose,
                               purpose_type,
                               reference
                        FROM hrm_movement_register
                        WHERE movement_date = :movement_date 
                     '''
        my_query = query_db(oracle_sql, {'movement_date': l_movement_date})
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def upd_movement_register(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_movement_id = l_dic["movement_id"]
        l_movement_date = l_dic["movement_date"]
        l_out_dttm = l_dic["out_dttm"]
        l_in_dttm = l_dic["in_dttm"]
        l_location_from = l_dic["location_from"]
        l_location_to = l_dic["location_to"]
        l_purpose = l_dic["purpose"]
        cur_oracle.callproc("front_end_support_tool.upd_movement_register",
                            [l_movement_id,l_movement_date,l_out_dttm,l_in_dttm,l_location_from,l_location_to,l_purpose])
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        con.commit()
        con.close()
        return HttpResponse(True)

def del_movement_register(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()
        l_movement_id = l_dic["movement_id"]
        cur_oracle.callproc("front_end_support_tool.del_movement_register",
                            [l_movement_id])
        l_list_of_tuples = l_dic.items()  # Dictionary to list of tuples
        con.commit()
        con.close()
        return HttpResponse(True)

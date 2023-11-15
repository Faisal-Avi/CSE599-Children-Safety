from django.shortcuts import render, HttpResponse
import cx_Oracle
import json, ast
from jsonmerge import merge
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

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
		
def employee_office_id_card(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print request.GET
        l_data = request.GET
        l_dic = l_data.dict()
        oracle_sql = '''SELECT hed.employee_full_name,
							   hed.auto_formated_id,
							   hed.desig_name,
							   hed.dept_name,
							   TO_CHAR(hed.joining_date, 'DD-MON-RRRR') joining_date ,
							   hed.blood_group,
							   hed.permanent_address,
							   hed.home_phone,
							   hed.nin,
							   'http://103.199.108.43/GROUP/EMPLOYEEPHOTO'
								|| hed.employee_id
								|| NVL (
								  hr_admin_pack.get_max_attachment_sl (hed.employee_id),
								  1)
								|| '.JPG'
								image_url
						FROM hrm_employee_detail hed
						WHERE hed.active_ind = 'Y'
						AND hed.employee_category_id = 4041
						UNION ALL
						SELECT hed.employee_full_name,
							   hed.auto_formated_id,
							   hed.desig_name,
							   hed.dept_name,
							   TO_CHAR(hed.joining_date, 'DD-MON-RRRR') joining_date ,
							   hed.blood_group,
							   hed.permanent_address,
							   hed.home_phone,
							   hed.nin,
							   'http://103.199.108.43/ACCESSORIES/EMPLOYEEPHOTO'
								|| hed.employee_id
								|| NVL (
								  hr_admin_pack.get_max_attachment_sl (hed.employee_id),
								  1)
								|| '.JPG'
								image_url
						FROM hrm_employee_detail@dblink_accs hed
						WHERE hed.active_ind = 'Y'
						AND hed.employee_category_id = 4041
						UNION ALL
						SELECT hed.employee_full_name,
							   hed.auto_formated_id,
							   hed.desig_name,
							   hed.dept_name,
							   TO_CHAR(hed.joining_date, 'DD-MON-RRRR') joining_date ,
							   hed.blood_group,
							   hed.permanent_address,
							   hed.home_phone,
							   hed.nin,
							   'http://103.199.108.43/FOOD/EMPLOYEEPHOTO'
								|| hed.employee_id
								|| NVL (
								  hr_admin_pack.get_max_attachment_sl (hed.employee_id),
								  1)
								|| '.JPG'
								image_url
						FROM hrm_employee_detail@dblink_food hed
						WHERE hed.active_ind = 'Y'
						AND hed.employee_category_id = 4041
                     '''
        my_query = query_db(oracle_sql)
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)

def employee_id_card(request):
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print request.GET
        l_data = request.GET
        l_dic = l_data.dict()
        l_emp_id = l_dic["employee_id"]
        l_reference = l_dic["reference"]		
        oracle_sql = '''SELECT employee_full_name,
							   auto_formated_id,
							   desig_name,
							   dept_name,
							   joining_date ,
							   blood_group,
							   permanent_address,
							   home_phone,
							   nin,
							   image_url,
							   employee_id,
							   reference
						FROM       
						(
							SELECT hed.employee_full_name,
								   hed.auto_formated_id,
								   hed.desig_name,
								   hed.dept_name,
								   TO_CHAR(hed.joining_date, 'DD-MON-RRRR') joining_date ,
								   hed.blood_group,
								   hed.permanent_address,
								   hed.home_phone,
								   hed.nin,
								   'http://103.199.108.43/GROUP/EMPLOYEEPHOTO'
									|| hed.employee_id
									|| NVL (
									  hr_admin_pack.get_max_attachment_sl (hed.employee_id),
									  1)
									|| '.JPG'
									image_url,
									hed.employee_id,
									'GROUP' reference
							FROM hrm_employee_detail hed
							WHERE hed.active_ind = 'Y'
							UNION ALL
							SELECT hed.employee_full_name,
								   hed.auto_formated_id,
								   hed.desig_name,
								   hed.dept_name,
								   TO_CHAR(hed.joining_date, 'DD-MON-RRRR') joining_date ,
								   hed.blood_group,
								   hed.permanent_address,
								   hed.home_phone,
								   hed.nin,
								   'http://103.199.108.43/ACCESSORIES/EMPLOYEEPHOTO'
									|| hed.employee_id
									|| NVL (
									  hr_admin_pack.get_max_attachment_sl (hed.employee_id),
									  1)
									|| '.JPG'
									image_url,
									hed.employee_id,
									'ACCESSORIES' reference
							FROM hrm_employee_detail@dblink_accs hed
							WHERE hed.active_ind = 'Y'
							UNION ALL
							SELECT hed.employee_full_name,
								   hed.auto_formated_id,
								   hed.desig_name,
								   hed.dept_name,
								   TO_CHAR(hed.joining_date, 'DD-MON-RRRR') joining_date ,
								   hed.blood_group,
								   hed.permanent_address,
								   hed.home_phone,
								   hed.nin,
								   'http://103.199.108.43/FOOD/EMPLOYEEPHOTO'
									|| hed.employee_id
									|| NVL (
									  hr_admin_pack.get_max_attachment_sl (hed.employee_id),
									  1)
									|| '.JPG'
									image_url,
									hed.employee_id,
									'FOOD' reference
							FROM hrm_employee_detail@dblink_food hed
							WHERE hed.active_ind = 'Y'
						)
						WHERE reference = :reference
						AND employee_id = :employee_id
                     '''
        my_query = query_db(oracle_sql, {'employee_id': l_emp_id,'reference': l_reference})
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)
		
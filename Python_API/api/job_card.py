from django.shortcuts import render, HttpResponse
import cx_Oracle
import json, ast

rows = [ (1,"First" ),
         (2,"Second" ) ]
         
def query_db(query, args=(), one=False):
    db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
    con = cx_Oracle.connect(db_connection_info)
    cur_oracle = con.cursor()
    cur_oracle.execute(query, args)
    r = [dict((cur_oracle.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur_oracle.fetchall()]
    cur_oracle.connection.close()
    return (r[0] if r else None) if one else r         
def job_card_rpt(request):    
    if request.method == 'GET':
        db_connection_info = 'bottomerp/dekkkoerp#sdi#@103.199.108.43/dcoproddb1'
        con = cx_Oracle.connect(db_connection_info)
        cur_oracle = con.cursor()
        print(request.GET)
        l_data = request.GET
        l_dic = l_data.dict()  #queryDict tO Dictionary
        l_emp_id = l_dic["employee_id"]
        l_list_of_tuples = l_dic.items() #Dictionary to list of tuples
        con.commit()
        con.close()
        oracle_sql = '''SELECT employee_id,
                               joining_date,
                               duration,
                               duty_date,
                               duty_day,
                               in_time,
                               out_time,
                               late_min,
                               late
                        FROM       
                            (
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'Dy') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late
                                FROM hrm_duty_roster hdr,
                                     hrm_employee_detail hed,
                                     hrm_shift hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                             NULL
                                       END late
                                FROM hrm_duty_roster@dblink_food hdr,
                                     hrm_employee_detail@dblink_food hed,
                                     hrm_shift@dblink_food hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                                UNION ALL
                                SELECT hed.auto_formated_id employee_id,
                                       hed.employee_full_name,
                                       hed.desig_name,
                                       hed.company,
                                       hed.dept_name,
                                       TO_CHAR(hed.joining_date, 'DD/MM/RRRR') joining_date,
                                       hrm_supp.calc_duration_short(hed.joining_date, SYSDATE) duration,
                                       TO_CHAR(hdr.duty_date, 'DD Mon') duty_date,
                                       TO_CHAR(hdr.duty_date, 'Day') duty_day,
                                       TO_CHAR(hdr.in_dttm, 'HH:MI AM') in_time,
                                       TO_CHAR(hdr.out_dttm, 'HH:MI AM') out_time,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                                  TO_CHAR(FLOOR (
                                                       (  hdr.in_dttm
                                                        - (  TO_DATE (
                                                                   TO_CHAR (hdr.duty_date, 'ddmmrr')
                                                                || hs.shift_start_hour
                                                                || hs.shift_start_minute,
                                                                'ddmmrrhh24mi')
                                                           - CASE
                                                                WHEN TO_CHAR (hdr.in_dttm, 'SS') = 0
                                                                THEN
                                                                   (1 / 86400)
                                                                ELSE
                                                                   0
                                                             END))
                                                     * 24
                                                     * 60))
                                            ELSE NULL
                                       END late_min,
                                       CASE WHEN hdr.in_dttm > TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| 16,'ddmmrrhh24mi') THEN
                                              fd_day_diff (TO_DATE (TO_CHAR (hdr.duty_date, 'ddmmrr')|| hs.shift_start_hour|| hs.shift_start_minute,'ddmmrrhh24mi'),hdr.in_dttm)
                                       ELSE
                                              NULL
                                       END late
                                FROM hrm_duty_roster@dblink_food hdr,
                                     hrm_employee_detail@dblink_food hed,
                                     hrm_shift@dblink_food hs
                                WHERE hdr.employee_id = hed.employee_id
                                AND TO_CHAR(hdr.duty_date, 'MMRRRR') = TO_CHAR(SYSDATE, 'MMRRRR')
                                AND hdr.shift_id = hs.shift_id(+)
                            )
                        WHERE employee_id = :employee_id
                        ORDER BY duty_date''' 
        my_query = query_db(oracle_sql, {'employee_id': l_emp_id} )
        l_json_output = json.dumps(my_query)
        return HttpResponse(l_json_output)
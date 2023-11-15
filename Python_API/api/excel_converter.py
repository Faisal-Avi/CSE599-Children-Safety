import xlwt
from django.http import HttpResponse
from django.contrib.auth.models import User
import cx_Oracle

def excel_view(request):
    db_connection_info = 'bottomerp/OurSDi3RpT3#mB2@192.168.66.24/dcoproddb1'
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

    header = ['Region Target',]

    for col_num in range(len(header)):
        ws.write(row_num, col_num, header[col_num], font_style)

    columns = ['SL', 'REGION',]

    oracle_sql_1 =   '''select distinct mrti.item_code
                        from mkt_region_target@dblink_food mrt,
                             mkt_region_target_itm@dblink_food mrti,
                             mkt_national_target@dblink_food mnt
                        where mrt.national_target_id = mnt.national_target_id
                        and mrt.region_target_id = mrti.region_target_id
                        and mrt.national_target_id = :p_ntid
                        order by 1'''

    cur.execute(oracle_sql_1, {'p_ntid':217})

    items = cur.fetchall()

    for m in items:
        columns.append(m)

    for col_num in range(len(columns)):
        ws.write(1, col_num, columns[col_num], font_style)

    oracle_sql_2 = '''select rownum,
                             region_name
                      from (
                        select distinct region_name
                        from mkt_region_target@dblink_food mrt,
                             mkt_region_target_itm@dblink_food mrti,
                             mkt_national_target@dblink_food mnt
                        where mrt.national_target_id = mnt.national_target_id
                        and mrt.region_target_id = mrti.region_target_id
                        and mrt.national_target_id = :p_ntid
                        order by 1)'''

    cur.execute(oracle_sql_2, {'p_ntid':217})

    regions = cur.fetchall()
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    row_num = 1
    for region in regions:
        row_num = row_num + 1
        for col_num in range(len(region)):
            ws.write(row_num, col_num, region[col_num],font_style)

    oracle_sql_3 =   '''select region_name,
                               item_code,
                               target_quantity
                        from mkt_region_target@dblink_food mrt,
                             mkt_region_target_itm@dblink_food mrti,
                             mkt_national_target@dblink_food mnt
                        where mrt.national_target_id = mnt.national_target_id
                        and mrt.region_target_id = mrti.region_target_id
                        and mrt.national_target_id = :p_ntid
                        order by 1'''

    cur.execute(oracle_sql_3, {'p_ntid': 217})

    regions_itmes_qty = cur.fetchall()
    r = 1
    c = 1
    for i in items:
        c = c + 1
        for j in regions:
            r = r + 1
            for k in regions_itmes_qty:
                if i[0] == k[1]:
                    if j[1] == k[0]:
                        ws.write(r, c, k[2] ,font_style)
        r = 1

    wb.save(response)
    return response
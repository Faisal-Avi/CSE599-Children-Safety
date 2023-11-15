import xlwt
from django.http import HttpResponse
from django.contrib.auth.models import User
import cx_Oracle

def excel_view(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    header = ['Excel Header',]

    for col_num in range(len(header)):
        ws.write(row_num, col_num, header[col_num], font_style)

    columns = ['Username', 'First name', 'Last name', 'Email address', ]

    for col_num in range(len(columns)):
        ws.write(1, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    db_connection_info = 'bottomerp/dekkkoerp#sdi#@192.168.66.24/dcoproddb1'
    con = cx_Oracle.connect(db_connection_info)
    cur = con.cursor()

    oracle_sql = '''SELECT t.trade_qty,
                           iu.short_name trade_unit,
                           oi.item_name offer_item_name,
                           t.offer_qty
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

    cur.execute(oracle_sql)

    rows = cur.fetchall()
    row_num = 1
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
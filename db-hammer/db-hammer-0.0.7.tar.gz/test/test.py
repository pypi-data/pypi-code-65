from db_hammer.mysql import MySQLConnection

db_conf = {
    "host": "172.18.20.170",
    "user": "gd_dc",
    "pwd": "gd_dc$2020",
    "db_name": "gd_dc"
}

with MySQLConnection(**db_conf) as db:
    i_sql = db.gen_insert_dict_sql(dict_data={
        "name": "小白",
        "sex": "男",
        "age": "20",
        "address": "上海市虹口区",
    }, table_name="t_student")

    db.execute(i_sql)
    db.commit()

    rs = db.select_dict_list(sql="select * from t_student")
    print(rs)

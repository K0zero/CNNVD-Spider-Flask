from flask import Flask, render_template, jsonify, request
import pymysql
import hashlib
import json

app = Flask(__name__)


# md5加密
def md5_encode(text):
    # 创建一个 MD5 对象
    md5 = hashlib.md5()
    # 将文本转换为字节类型并进行加密
    md5.update(text.encode('utf-8'))
    # 获取加密后的结果
    encrypted_text = md5.hexdigest()
    return encrypted_text


# MySQL 配置
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DB = 'pearadminflask'


# 创建 MySQL 连接
def create_mysql_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


# 查询数据库
def query_database(sql):
    conn = create_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    finally:
        conn.close()


# 插入数据
def insert_data(sql, values):
    conn = create_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("插入数据失败:", e)
        return False
    finally:
        conn.close()


# 更新数据
def update_data(sql, values):
    conn = create_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("修改数据失败:", e)
        return False
    finally:
        conn.close()


# 删除数据
def delete_data(sql):
    conn = create_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/reg')
def reg():
    return render_template("reg.html")


@app.route('/login', methods=['POST'])
def login():
    name = request.form.get("name")
    password = request.form.get("password")
    sql = f"select name,admin from user where name = '{name}' and password = '{password}'"
    check = query_database(sql)
    if len(check) > 0:
        token = md5_encode(name)
        return jsonify({'code': '200', 'msg': 'Login ok', 'token': token, 'admin': check[0]["admin"]})
    else:
        return jsonify({'code': '500', 'msg': 'User not exists or password error.'})


@app.route('/toReg', methods=['POST'])
def toReg():
    name = request.form.get("name")
    phone = request.form.get("phone")
    password = request.form.get("password")

    # 查询有重复的账号或者邮箱
    sql = f"select count(0) num from user where name = '{name}' or phone = '{phone}'"
    check = query_database(sql)
    if check[0]["num"] > 0:
        return jsonify({'code': '500', 'msg': 'User already exists'})

    # 插入记录
    sql = 'INSERT INTO user (name, phone, password, addTime) VALUES (%s, %s, %s, now())'
    values = (name, phone, password)

    if insert_data(sql, values):
        token = md5_encode(name)
        return jsonify({'code': '200', 'msg': 'User created successfully', 'token': token})
    else:
        return jsonify({'code': '500', 'msg': 'Failed to create user'})

    if len(check) > 0:
        token = md5_encode(name)
        return jsonify({'code': '200', 'msg': 'Login ok', 'token': token})
    else:
        return jsonify({'code': '500', 'msg': 'User not exists or password error.'})


@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/report")
def report():
    sql = f'select count(0) num from user'
    userNum = query_database(sql)[0]['num']
    sql = f'select count(0) num from vulnerability'
    vulNum = query_database(sql)[0]['num']
    sql = f"select count(0) num from vulnerability where DATE_FORMAT(发布时间 ,'%Y-%m') = DATE_FORMAT(now() ,'%Y-%m')"
    mNum = query_database(sql)[0]['num']
    sql = f"select count(0) num from vulnerability where DATE_FORMAT(发布时间 ,'%Y-%m-%d') = DATE_FORMAT(now() ,'%Y-%m-%d')"
    dNum = query_database(sql)[0]['num']
    sql = f"select DATE_FORMAT(发布时间 ,'%Y-%m') date,count(0) num from vulnerability  GROUP BY DATE_FORMAT(发布时间 ,'%Y-%m')  order by DATE_FORMAT(发布时间 ,'%Y-%m') "
    dateList = query_database(sql)
    sql = f"select if(危害等级='','未知',危害等级) name,count(0) value from vulnerability  GROUP BY 危害等级 "
    危害等级List = query_database(sql)
    sql = f"select if(漏洞类型='','未知',漏洞类型) name,count(0) value from vulnerability  GROUP BY 漏洞类型 "
    漏洞类型List = query_database(sql)
    sql = f"select if(威胁类型='','未知',威胁类型) name,count(0) value from vulnerability  GROUP BY 威胁类型 "
    威胁类型List = query_database(sql)
    return render_template("report.html", userNum=userNum, vulNum=vulNum, mNum=mNum, dNum=dNum, dateList=dateList,
                           危害等级List=危害等级List, 漏洞类型List=漏洞类型List, 威胁类型List=威胁类型List)


@app.route("/userList")
def userList():
    return render_template("userList.html")


@app.route("/getUserList", methods=['POST'])
def getUserList():
    sql = f"select id,name,insert(phone,4,6,'******') phone,insert(password,2,4,'****') password,DATE_FORMAT(addTime, '%Y-%m-%d') addTime,admin from user where 1 = 1"
    name = request.form.get("name")
    phone = request.form.get("phone")
    time1 = request.form.get("time1")
    time2 = request.form.get("time2")
    if name != "":
        sql += f" and name like '%{name}%'"
    if phone != "":
        sql += f" and phone like '%{phone}%'"
    if time1 != "":
        sql += f" and addTime >= '{time1}'"
    if time2 != "":
        sql += f" and addTime <= '{time2} 23:59:59'"

    sql1 = sql
    page = int(request.form.get("page"))
    pageSize = int(request.form.get("pageSize"))
    sql1 += " order by id desc limit " + str((page - 1) * pageSize) + "," + str(pageSize) + ""
    datas = query_database(sql1)
    start_index = sql.find("from")
    sql2 = 'select count(0) as count ' + sql[start_index:]
    count = int(query_database(sql2)[0]['count'])
    return jsonify({'code': '200', 'msg': 'ok', 'data': {'list': datas, 'page': page, 'count': count}})


@app.route("/delUser", methods=['POST'])
def delUser():
    ids = request.form.get("ids")
    sql = f"delete from user where id in ({ids})"
    delete_data(sql)
    return jsonify({'code': '200', 'msg': 'ok'})


@app.route("/getUser", methods=['POST'])
def getUser():
    id = request.form.get("id")
    sql = f"select id,name,phone,password,DATE_FORMAT(addTime, '%Y-%m-%d') addTime,admin from user where id = {id}"
    return jsonify({'code': '200', 'msg': 'ok', 'data': query_database(sql)[0]})


@app.route("/addOrEditUser", methods=['POST'])
def addOrEditUser():
    id = int(request.form.get("id"))
    name = request.form.get("name")
    phone = request.form.get("phone")
    password = request.form.get("password")
    addTime = request.form.get("addTime")
    admin = request.form.get("admin")
    if id > 0:
        sql = "UPDATE user SET name=%s, phone=%s, password=%s, addTime=%s, admin=%s WHERE id=%s"
        values = (name, phone, password, addTime, admin, id)
        update_result = update_data(sql, values)
    else:
        sql = "INSERT INTO user (name, phone, password, addTime, admin) VALUES (%s, %s, %s, %s, %s)"
        values = (name, phone, password, addTime, admin)
        insert_result = insert_data(sql, values)
    return jsonify({'code': '200', 'msg': 'ok'})


@app.route("/dataList")
def dataList():
    return render_template("dataList.html")


@app.route("/getDataList", methods=['POST'])
def getDataList():
    sql = f"select id,CNNVD,危害等级,CVE编号,漏洞类型,DATE_FORMAT(发布时间, '%Y-%m-%d') 发布时间,威胁类型,DATE_FORMAT(更新时间, '%Y-%m-%d') 更新时间,厂商,漏洞来源,漏洞公告,参考网址,受影响实体,补丁 from vulnerability where 1 = 1"
    cnnvd = request.form.get("cnnvd")
    time1 = request.form.get("time1")
    time2 = request.form.get("time2")
    if cnnvd != "":
        sql += f" and cnnvd like '%{cnnvd}%'"
    if time1 != "":
        sql += f" and 发布时间 >= '{time1}'"
    if time2 != "":
        sql += f" and 发布时间 <= '{time2}'"

    sql1 = sql
    page = int(request.form.get("page"))
    pageSize = int(request.form.get("pageSize"))
    sql1 += " order by id desc limit " + str((page - 1) * pageSize) + "," + str(pageSize) + ""
    datas = query_database(sql1)
    start_index = sql.find("from")
    sql2 = 'select count(0) as count ' + sql[start_index:]
    count = int(query_database(sql2)[0]['count'])
    return jsonify({'code': '200', 'msg': 'ok', 'data': {'list': datas, 'page': page, 'count': count}})


@app.route("/delData", methods=['POST'])
def delData():
    ids = request.form.get("ids")
    sql = f"delete from vulnerability where id in ({ids})"
    delete_data(sql)
    return jsonify({'code': '200', 'msg': 'ok'})


@app.route("/getData", methods=['POST'])
def getData():
    id = request.form.get("id")
    sql = f"select id,CNNVD,危害等级,CVE编号,漏洞类型,DATE_FORMAT(发布时间, '%Y-%m-%d') 发布时间,威胁类型,DATE_FORMAT(更新时间, '%Y-%m-%d') 更新时间,厂商,漏洞来源,漏洞公告,参考网址,受影响实体,补丁 from vulnerability where id = {id}"
    return jsonify({'code': '200', 'msg': 'ok', 'data': query_database(sql)[0]})


@app.route("/addOrEditData", methods=['POST'])
def addOrEditData():
    id = int(request.form.get("id"))
    cnnvd = request.form.get("CNNVD")
    level = request.form.get("危害等级")
    cve = request.form.get("CVE编号")
    vul_type = request.form.get("漏洞类型")
    publish_time = request.form.get("发布时间")
    threat_type = request.form.get("威胁类型")
    update_time = request.form.get("更新时间")
    vendor = request.form.get("厂商")
    source = request.form.get("漏洞来源")
    advisory = request.form.get("漏洞公告")
    reference = request.form.get("参考网址")
    affected_entity = request.form.get("受影响实体")
    patch = request.form.get("补丁")
    if id > 0:
        sql = "UPDATE vulnerability SET CNNVD=%s, `危害等级`=%s, `CVE编号`=%s, `漏洞类型`=%s, `发布时间`=%s, `威胁类型`=%s, `更新时间`=%s, `厂商`=%s, `漏洞来源`=%s, `漏洞公告`=%s, `参考网址`=%s, `受影响实体`=%s, `补丁`=%s WHERE id=%s"
        values = (
            cnnvd, level, cve, vul_type, publish_time, threat_type, update_time, vendor, source, advisory, reference,
            affected_entity, patch, id)
        update_result = update_data(sql, values)
    else:
        sql = "INSERT INTO vulnerability (CNNVD, `危害等级`, `CVE编号`, `漏洞类型`, `发布时间`, `威胁类型`, `更新时间`, `厂商`, `漏洞来源`, `漏洞公告`, `参考网址`, `受影响实体`, `补丁`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            cnnvd, level, cve, vul_type, publish_time, threat_type, update_time, vendor, source, advisory, reference,
            affected_entity, patch)
        insert_result = insert_data(sql, values)
    return jsonify({'code': '200', 'msg': 'ok'})


if __name__ == '__main__':
    app.run()

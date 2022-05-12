import flask
import pandas as pd
# test
from sqlalchemy import create_engine
cnx = create_engine('mysql+pymysql://root:tommyisthebest@localhost:3306/dbproj', echo=False)

def verify(username: str, cnx):
    result = pd.read_sql_query("""
        SELECT 1
        FROM user
        WHERE uname='{username}';
    """.format(username=username),cnx)
    # print(result)
    if (result.empty):
        print("Not found!")
        return ""
    else:
        print("FOUND!")
    return username

def check_pw(username: str, pw_string: str, cnx):
    result = pd.read_sql_query("""
        SELECT 1
        FROM user
        WHERE uname='{username}' AND password='{pw_string}';
    """.format(username=username, pw_string=pw_string), cnx)

    if (result.empty):
        print("Invalid username/password")
        return False
    print("success!")
    return True

def getID(username, cnx) -> int:
    result = pd.read_sql_query("""
        SELECT uid
        FROM user
        WHERE uname = '{username}'
    """.format(username=username), cnx)
    # print(result['uid'][0])
    if (result.empty):
        return None
    return result['uid'][0]

def getName(uid: int, cnx):
    # print(uid)
    result = pd.read_sql_query("""
        SELECT first_name, last_name
        FROM user
        WHERE uid={uid}
    """.format(uid=uid), cnx)
    if (result.empty):
        return None, None
    # print(result['first_name'][0], result['last_name'][0])
    return result['first_name'][0], result['last_name'][0]

def getAnswers(uid, cnx):
    result = pd.read_sql_query("""
        SELECT *
        FROM answers
        WHERE uid={uid}
    """.format(uid=uid), cnx)
    if (result.empty):
        return None
    # print(result)
    return result

def getQuestions(uid, cnx):
    result = pd.read_sql_query("""
        SELECT *
        FROM questions
        WHERE uid={uid}
    """.format(uid=uid), cnx)
    if (result.empty):
        return None
    # print(result)
    return result

def check_status()->str:
    cookie = flask.request.cookies.get('user')
    if (cookie != None): return cookie
    return ""

def getStats(uid, cnx):
    result = pd.read_sql_query ("""
        SELECT view_stats.*,user.last_name,user.first_name 
        FROM view_stats 
        INNER JOIN user ON view_stats.uid = user.uid
        WHERE view_stats.uid = {uid}
    """.format(uid=uid), cnx)
    if (result.empty):
        return None
    # print(result)
    return result

def getCategories(cnx):
    result = pd.read_sql_query("""
        SELECT cname
        FROM category
    """, cnx)
    if (result.empty):
        return None
    # print(result)
    return result



# getCategories(cnx)

# getQuestions(1,cnx)

# getName(5,cnx)
# getID("test", cnx)

# verify("test",cnx)
# check_pw(verify("aa",cnx), "ss", cnx)
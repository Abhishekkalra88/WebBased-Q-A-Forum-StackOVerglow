# -*- coding: utf-8 -*-
"""
Created on Tue May  3 16:42:22 2022

@author: Abhishek
"""

import flask
from flask import render_template, redirect, url_for, request
import datetime
from datetime import date
# import mysql.connector
import pandas as pd
from helper import getAnswers,getID,getName,getQuestions,verify, check_pw, check_status, getStats, getCategories
# import pymysql
from sqlalchemy import create_engine, true
cnx = create_engine('mysql+pymysql://root:tommyisthebest@localhost:3306/dbproj', echo=False)

# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="tommyisthebest",
#     database="bakery"
# )

# ------------------------------
# ADD like count
# Optimize functions
# ------------------------------


app = flask.Flask(__name__,static_folder='static')           


@app.route('/', methods=['GET','POST'])
def splash():
    if request.method == 'POST':
        if request.form['search']:
            return redirect(url_for('table_search', keyword=request.form['search']))
    return render_template('new_splash.html')

# Route for handling the login page logic   
@app.route('/login', methods=['GET', 'POST'])
def login():
    # check and redirect if cookie exists
    cookie = check_status()
    # print(cookie)
    if (cookie != ""):
        return redirect(url_for('logged_in', username=cookie))
    error = None

    # if user tries to log in
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        res = verify(username, cnx)
        # in practice it is not a good idea to reveal which one is wrong,
        # but this is just for demo purposes
        if (res == ""):
            error = 'Username does not exist'
            return render_template('login.html', error=error)

        if(check_pw(res, password, cnx) == False):
            error = 'Password incorrect'
            return render_template('login.html', error=error)
        else:
            # set cookie and redirect to logged in page
            
            resp = flask.make_response(redirect(url_for('logged_in', username=username)))
            exp_time = datetime.datetime.now() + datetime.timedelta(days=7)
            resp.set_cookie('user', request.form['username'], expires=exp_time)
            return resp

    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET','POST'])
def signup():
    # when user submits signup form
    if request.method == "POST":
        # should query check if any field is taken
        first_name = request.form.get("fname")
        last_name = request.form.get("lname")
        username = request.form.get("uname")
        email = request.form.get("email")
        password = request.form.get("pw")
        bio = request.form.get("bio")
        df = {
            'first_name': [first_name],
            'last_name': [last_name], 
            'uname':[username], 
            'email':[email], 
            'password':[password],
            'Presence':[0],
            'bio':[bio]
        }
        # convert to a dataframe
        df = pd.DataFrame(data=df)
        # insert
        success = df.to_sql('user',cnx,'dbproj', if_exists='append', index=False)
        # print(success)
        # set cookie and redirect
        resp = flask.make_response(redirect(url_for('logged_in', username=username)))
        exp_time = datetime.datetime.now() + datetime.timedelta(days=7)
        resp.set_cookie('user', username, expires=exp_time)
        return resp
    
    return render_template('signup.html')



@app.route('/QA/<qid>/<aid>', methods=['GET', 'POST'])
def qa(qid,aid):
    print(aid,qid)
    cookie = check_status()
    uid = getID(cookie, cnx)
    string_in_string = f"""SELECT * FROM questions JOIN user ON user.uid=questions.uid WHERE qid = {qid}"""
    qtable = pd.read_sql_query (string_in_string, cnx)
    string_in_string = f"""SELECT * FROM answers JOIN user ON user.uid=answers.uid WHERE qid = {qid}"""
    atable = pd.read_sql_query (string_in_string, cnx)
    if request.method == 'GET':
        return render_template('layouts/base.html', qa=True, qtable=qtable, atable=atable, username=cookie)
    if request.method == 'POST':
        # Limitation: user can like/dislike as many times as they want.
        print("received post request for qid/aid ", qid, aid)
        if "search" in request.form:
            return redirect(url_for('table_search', keyword=request.form['search']))
        if "LikeQ" in request.form:
            print("Liking a question")
            df = {
                'uid':[uid],
                'qid':[qid],
                'aid':[None],
                'upvote':[1],
                'downvote':[0],
                'best':[0]
            }
            df = pd.DataFrame(data=df)
            success = df.to_sql('transactions', cnx,'dbproj', if_exists = 'append', chunksize = 1000, index = False)
            print(success)
            return render_template('layouts/base.html', qa=True, qtable=qtable, atable=atable, username=cookie)
        if "DislikeQ" in request.form:
            print("disliking a question")
            df = {
                'uid':[uid],
                'qid':[qid],
                'aid':[None],
                'upvote':[0],
                'downvote':[1],
                'best':[0]
            }
            df = pd.DataFrame(data=df)
            success = df.to_sql('transactions', cnx,'dbproj', if_exists = 'append', chunksize = 1000, index = False)
            print(success)
            return render_template('layouts/base.html', qa=True, qtable=qtable, atable=atable, username=cookie)
        if "LikeA" in request.form:
            print("liking an answer")
            df = {
                'uid':[uid],
                'qid':[qid],
                'aid':[aid],
                'upvote':[1],
                'downvote':[0],
                'best':[0]
            }
            df = pd.DataFrame(data=df)
            success = df.to_sql('transactions', cnx,'dbproj', if_exists = 'append', chunksize = 1000, index = False)
            print(success)
            return render_template('layouts/base.html', qa=True, qtable=qtable, atable=atable, username=cookie)
        if "DislikeA" in request.form:
            print("disliking an answer")
            df = {
                'uid':[uid],
                'qid':[qid],
                'aid':[aid],
                'upvote':[0],
                'downvote':[1],
                'best':[0]
            }
            df = pd.DataFrame(data=df)
            success = df.to_sql('transactions', cnx,'dbproj', if_exists = 'append', chunksize = 1000, index = False)
            print(success)
            return render_template('layouts/base.html', qa=True, qtable=qtable, atable=atable, username=cookie)

        if "answer" in request.form:
            if request.form['answer'] != "":
            # to be fixed: asker/answerer name disappears after posting
                print("User typed in", request.form['answer'])
                df = {
                    'qid':[qid],
                    'uid':[uid],
                    'body': [request.form['answer']],
                    'date': [date.today().strftime("%Y-%m-%d")]
                }
                df = pd.DataFrame(data=df)
                success = df.to_sql('answers', cnx,'dbproj', if_exists = 'append', chunksize = 1000, index = False)
                print(success)
                string_in_string = f"""SELECT * FROM questions where qid = {qid}"""
                qtable = pd.read_sql_query (string_in_string, cnx)
                string_in_string = f"""SELECT * FROM answers where qid = {qid}"""
                atable = pd.read_sql_query (string_in_string, cnx)
                #qid,uid,cid,title,body,date
                return render_template( "/layouts/base.html", qa=True, qtable=qtable, atable=atable, username=cookie)
        return render_template('layouts/base.html', qa=True, qtable=qtable, atable=atable, username=cookie)

@app.route('/table_search/<keyword>', methods=['GET', 'POST'])
def table_search(keyword):
    cookie = check_status()
    if request.method == 'POST':
        if "search" in request.form:
            return redirect(url_for('table_search', keyword=request.form['search']))
    if request.method == 'GET':
        string_in_string="""
        Select * from (
            SELECT MATCH(body) AGAINST('+{keyword}*'IN BOOLEAN MODE) AS Relevance,
            date,
            qid,
            aid,
            body
            FROM answers
            WHERE MATCH(body) AGAINST('+{keyword}*'IN BOOLEAN MODE)
        ) A
        ORDER BY RELEVANCE desc;
        """.format(keyword=keyword)
        df = pd.read_sql_query (string_in_string, cnx)
        string_in_string = """
        Select * from (
            SELECT MATCH(title) AGAINST('+{keyword}*'IN BOOLEAN MODE) AS Relevance,
            date,
            qid, 
            title
            FROM questions
            WHERE MATCH(title) AGAINST('+{keyword}*'IN BOOLEAN MODE)
        ) A
        ORDER BY RELEVANCE desc;
        """.format(keyword=keyword)
        df1 = pd.read_sql_query (string_in_string, cnx)
        return render_template( "layouts/base.html",table=df, table1 = df1, username=cookie, search=True)

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    cookie = check_status()
    if (cookie == ""):
        return redirect(url_for('splash'))
    # cookie = flask.request.cookies.get('user')
    if request.method == 'POST':
        print(request.form['search'])
        # print(request.form['question'])
        if request.form['search'] != "":
            return redirect(url_for('table_search', keyword=request.form['search']))
    uid = getID(cookie, cnx)
    df = getStats(uid,cnx)
    return render_template( "/layouts/base.html",table=df, username=cookie, profile=True)

@app.route('/post', methods=['GET','POST'])
def post():
    cookie = check_status()
    if (cookie == ""):
        print("cookie not found, redirecting")
        return redirect(url_for('splash'))
    uid = getID(cookie, cnx)
    categories = getCategories(cnx)
    if request.method == 'POST':
        if request.form['question'] != "":
        # print("Hey its a post")
        # print(request.form['category'])
        # print(request.form['question'])
            string_in_string = f"""Select cid from category where cname = '{request.form['category']}'"""
            cat = pd.read_sql_query (string_in_string, cnx)
            df = {
                'uid': [uid],
                'cid': [cat['cid'][0]],
                'title': [request.form['question']],
                'body': ['as stated in the title'],
                'date': [date.today().strftime("%Y-%m-%d")]
            }
            df = pd.DataFrame(data=df)
            success = df.to_sql('questions', cnx, 'dbproj', if_exists = 'append', chunksize = 1000, index = False)
            print(success)
            df = getAnswers(uid,cnx)
            df1 = getQuestions(uid,cnx)
            #qid,uid,cid,title,body,date
            return render_template( "/layouts/base.html", username=cookie, table=df, table1=df1, categories=categories, activity=True)
        df = getAnswers(uid,cnx)
        df1 = getQuestions(uid,cnx)
        return render_template( "/layouts/base.html", username=cookie, table=df, table1=df1, categories=categories, activity=True)
    print("it is not a post?")


@app.route('/<username>', methods=['GET', 'POST'])
def logged_in(username):
    # cookie = flask.request.cookies.get('user')
    cookie = check_status()
    if (cookie == ""):
        print("cookie not found, redirecting")
        return redirect(url_for('splash'))
    uid = getID(cookie, cnx)
    # print(cookie)
    categories = getCategories(cnx)
    if request.method == 'POST':
        print(request.form['search'])
        # print(request.form['question'])
        if request.form['search'] != "":
            return redirect(url_for('table_search', keyword=request.form['search']))
    if request.method == 'GET':
        df = getAnswers(uid,cnx)
        df1 = getQuestions(uid,cnx)
        return render_template( "/layouts/base.html",table=df,table1=df1, username=cookie, categories=categories, activity=True)

@app.route('/logout', methods = ['GET','POST'])
def logout():
    # fetch (?) and delete cookie, then redirect to splash page
    resp = flask.make_response(redirect(url_for('splash')))
    resp.delete_cookie('user')
    return resp





if __name__ == '__main__':
    app.run(debug=True, port=5000)    # app starts serving in debug mode on port 5000

from flask import Flask,render_template,request,session,redirect
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ibm_db
import jinja2
import re
from markupsafe import escape
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=abc.crt;UID=jmn22042;PWD=Q9mJneDaYMsgOLus",'','')
global total

global t_food 

global t_entertainment 

global t_business 

global t_rent

global t_EMI

global t_other 


    
print(conn)
print("connection successful...")
app = Flask(__name__)

app.secret_key = 'a'




#HOME--PAGE
@app.route("/")
def home():
    return render_template("home.html")


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        phoneno=request.form['phoneno']
        gender=request.form['sex']
        age=request.form['age']
        job=request.form['job']
        sql="SELECT * FROM USER WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        if account:
            print(username)
            return render_template('signup.html',msg="this name is already inserted")
           
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql="INSERT INTO USER VALUES (?,?,?,?,?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt,3,password)
            ibm_db.bind_param(prep_stmt,4,phoneno)
            ibm_db.bind_param(prep_stmt,5,gender)
            ibm_db.bind_param(prep_stmt,6,age)
            ibm_db.bind_param(prep_stmt,7,job)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            message = Mail(
                from_email='dhanushgoku997@gmail.com',
                to_emails=email,
                subject='extrack',
                html_content='<h1>Thank you for registering with ExTrack,you can now login and use the application</h1>'
                )
            try:
                    sg = SendGridAPIClient("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")
                    response = sg.send(message=message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
            except Exception as e:
                    print(e)
            
            return render_template('home.html',msg=msg)
    
    elif request.method=='GET':
        return render_template("signup.html")

@app.route("/signin")
def signin():
    return render_template("login.html")


@app.route('/login',methods=['GET','POST'])
def login():
    global userid
    msg = ''
    if request.method=='POST':
        email=request.form['Email']
        password=request.form['password']
        sql = "SELECT * FROM USER WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        dic = ibm_db.fetch_assoc(stmt)
        
        print(dic)
        if dic:
            session['loggedin'] = True
            session['id'] = dic['USERNAME']
            userid=  dic['USERNAME']
            session['username'] = dic['EMAIL']
            print(session['id'])
            print(session['username'])
            print(userid)
           
            return render_template("homepage.html")
        else:
            msg = 'Incorrect username / password !'
    return render_template("login.html", msg = msg)

@app.route("/add")
def adding():
    return render_template("add.html")

@app.route("/addexpense",methods=['GET','POST'])
def add():
    
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']

    insert_sql="INSERT INTO EXPENSE (USERNAME,DATE,EXPENSENAME,EXPENSEAMOUNT,PAYMENTMODE,CATEGORY) VALUES (?,?,?,?,?,?)"
    prep_stmt=ibm_db.prepare(conn,insert_sql)
    
    ibm_db.bind_param(prep_stmt,1,session['id'])
    ibm_db.bind_param(prep_stmt,2,date)
    ibm_db.bind_param(prep_stmt,3,expensename)
    ibm_db.bind_param(prep_stmt,4,amount)
    ibm_db.bind_param(prep_stmt,5,paymode)
    ibm_db.bind_param(prep_stmt,6,category)
   
    ibm_db.execute(prep_stmt)
   
    
    return redirect("/display")
   
    


@app.route("/display")
def history():
    expense = []
    sql = f"SELECT * FROM EXPENSE WHERE USERNAME='{session['id']}'" 

    stmt1= ibm_db.exec_immediate(conn,sql)
    print(stmt1)
   
    dictionary = ibm_db.fetch_both(stmt1)
    print(dictionary)
    print(session["username"],session['id'])
    while dictionary != False:
     expense.append(dictionary)
     dictionary = ibm_db.fetch_both(stmt1)
    if expense:
        return render_template("display.html",expense=expense)

@app.route("/edit/<userid>", methods = ['POST', 'GET' ])
def edit(userid):
    edit=[]
    print(userid)
    userid=userid
    sql=f"SELECT * FROM EXPENSE WHERE  USERID ={userid}"
    
    stmt1= ibm_db.exec_immediate(conn,sql)
  
    print(stmt1)
    dic= ibm_db.fetch_tuple(stmt1)
    
    print(userid)
    print(edit)
    return render_template("edit.html",dic=dic,userid=dic[0])

@app.route('/update/<name>/<userid>',methods=['GET','POST'])
def update(name,userid):
    if request.method=='POST':
     
      print(userid)
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['expenseamount']
      paymode= request.form['paymentmode']
      category = request.form['category']
      sql = f"SELECT * FROM EXPENSE WHERE USERNAME='{escape(name)}'"
      print(sql)
      stmt = ibm_db.exec_immediate(conn, sql)
      student = ibm_db.fetch_row(stmt)
      print ("The Name is : ",  student)
      if student:
         sql= f"UPDATE EXPENSE SET DATE =? , EXPENSENAME =?, EXPENSEAMOUNT = ? , PAYMENTMODE =?, CATEGORY = ?  WHERE  USERID ={escape(userid)} "
         print(sql)
         stmt1=ibm_db.prepare(conn,sql)  
      
         ibm_db.bind_param(stmt1,1,date)
         ibm_db.bind_param(stmt1,2,expensename)
         ibm_db.bind_param(stmt1,3,amount)
         ibm_db.bind_param(stmt1,4,paymode)
         ibm_db.bind_param(stmt1,5,category)

      
         ibm_db.execute(stmt1)
      
         expense = []
         sql = "SELECT * FROM EXPENSE"
         stmt = ibm_db.exec_immediate(conn, sql)
         dictionary = ibm_db.fetch_both(stmt)
         while dictionary != False:
          expense.append(dictionary)
          dictionary = ibm_db.fetch_both(stmt)
         if expense:
            print(dictionary)
            return redirect("/display")
   
  
@app.route('/delete/<name>/<userid>')
def delete(name,userid):
  sql = f"SELECT * FROM EXPENSE WHERE USERNAME='{escape(name)}'"
  print(sql)
  stmt = ibm_db.exec_immediate(conn, sql)
  student = ibm_db.fetch_row(stmt)
  print ("The Name is : ",  student)
  if student:
    sql = f"DELETE FROM EXPENSE WHERE USERID={escape(userid)}"
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)

    expense = []
    sql = "SELECT * FROM EXPENSE"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
      expense.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)
    if expense:
      return redirect("/display")

@app.route("/limit")
def limit():
    
    return redirect("/limit1")

@app.route("/limit1",methods=['GET','POST'])
def setlimit():
    if request.method=='POST':
    #  limit=[]
        limitamount = request.form['limitamount']
        
        month = request.form['month']
        sql="INSERT INTO LIMIT (USERNAME,MONTHAMOUNT,MONTH) VALUES (?,?,?) "
        print(sql)
        stmt1=ibm_db.prepare(conn,sql)  

        ibm_db.bind_param(stmt1,1,session['id'])
        ibm_db.bind_param(stmt1,2,limitamount)
        ibm_db.bind_param(stmt1,3,month)
        ibm_db.execute(stmt1)
        print('successfully inserted')
        return redirect("/limitln")
    else:
        return render_template("limit.html")
        
@app.route("/limitln")
def limitln():
      sql="SELECT MONTHAMOUNT FROM  LIMIT  ORDER BY LIMITID DESC LIMIT 1"
      stmt = ibm_db.exec_immediate(conn, sql)
      limit = ibm_db.fetch_tuple(stmt)
      print(limit)
      return render_template("limit.html",amount=limit[0])

@app.route("/today/<name>")
def today(name):
     
      print(name)
      texpense=[]
      expense=[]
      sql= f"SELECT DATE(date), SUM(EXPENSEAMOUNT) FROM EXPENSE WHERE USERNAME='{escape(name)}' AND DATE(DATE)=DATE(current timestamp)  GROUP BY DATE(date) ORDER BY DATE(date) "
      stmt1= ibm_db.exec_immediate(conn,sql)
      dictionary = ibm_db.fetch_both(stmt1)
      print(dictionary)
      while dictionary!=False:
        texpense.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt1)
       
      print(texpense)
      sql1=f"SELECT * FROM EXPENSE WHERE USERNAME = '{escape(name)}'"
      stmt= ibm_db.exec_immediate(conn,sql1)
      dictionary1 = ibm_db.fetch_both(stmt)
      print(dictionary1)
      while dictionary1!=False:
         expense.append(dictionary1)
         dictionary1= ibm_db.fetch_both(stmt)
      print(expense)
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          print(x["EXPENSEAMOUNT"])
          total =total+ int(x["EXPENSEAMOUNT"])
          if x["CATEGORY"] == "food":
              t_food=t_food+int(x["EXPENSEAMOUNT"])
            
          elif x["CATEGORY"] == "entertainment":
              t_entertainment  += int(x["EXPENSEAMOUNT"])
        
          elif x["CATEGORY"] == "business":
              t_business  +=int(x["EXPENSEAMOUNT"])
          elif x["CATEGORY"]  == "rent":
              t_rent  += int(x["EXPENSEAMOUNT"])
           
          elif x["CATEGORY"] == "EMI":
              t_EMI  += int(x["EXPENSEAMOUNT"])
         
          elif x["CATEGORY"]  == "other":
              t_other  += int(x["EXPENSEAMOUNT"])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)
      print(texpense)
      print(expense)

     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

@app.route("/month/<name>")
def month(name):
      
      texpense=[]
      expense=[]
      sql= f"SELECT DATE(date), SUM(EXPENSEAMOUNT) FROM EXPENSE WHERE USERNAME='{escape(name)}' AND MONTH(DATE)=MONTH(current timestamp)  GROUP BY DATE(date) ORDER BY DATE(date) "
      stmt1= ibm_db.exec_immediate(conn,sql)
      dictionary = ibm_db.fetch_both(stmt1)
      print(dictionary)
      while dictionary!=False:
        texpense.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt1)
       
      print(texpense)
      sql1=f"SELECT * FROM EXPENSE WHERE USERNAME = '{escape(name)}'"
      stmt= ibm_db.exec_immediate(conn,sql1)
      dictionary1 = ibm_db.fetch_both(stmt)
      print(dictionary1)
      while dictionary1!=False:
         expense.append(dictionary1)
         dictionary1= ibm_db.fetch_both(stmt)
      print(expense)
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          print(x["EXPENSEAMOUNT"])
          total =total+ int(x["EXPENSEAMOUNT"])
          if x["CATEGORY"] == "food":
              t_food=t_food+int(x["EXPENSEAMOUNT"])
            
          elif x["CATEGORY"] == "entertainment":
              t_entertainment  += int(x["EXPENSEAMOUNT"])
        
          elif x["CATEGORY"] == "business":
              t_business  +=int(x["EXPENSEAMOUNT"])
          elif x["CATEGORY"]  == "rent":
              t_rent  += int(x["EXPENSEAMOUNT"])
           
          elif x["CATEGORY"] == "EMI":
              t_EMI  += int(x["EXPENSEAMOUNT"])
         
          elif x["CATEGORY"]  == "other":
              t_other  += int(x["EXPENSEAMOUNT"])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)
      print(texpense)
      print(expense)

     
      return render_template("month.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
      

@app.route("/year/<name>")
def year(name):
      print(name)
      texpense=[]
      expense=[]
      sql= f"SELECT DATE(date), SUM(EXPENSEAMOUNT) FROM EXPENSE WHERE USERNAME='{escape(name)}' AND YEAR(DATE)=YEAR(current timestamp)  GROUP BY DATE(date) ORDER BY DATE(date) "
      stmt1= ibm_db.exec_immediate(conn,sql)
     
      dictionary = ibm_db.fetch_both(stmt1)
      print(dictionary)
      while dictionary!=False:
        texpense.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt1)
       
      print(texpense)
      sql1=f"SELECT * FROM EXPENSE WHERE USERNAME = '{escape(name)}'"
      stmt= ibm_db.exec_immediate(conn,sql1)
      dictionary1 = ibm_db.fetch_both(stmt)
      print(dictionary1)
      while dictionary1!=False:
         expense.append(dictionary1)
         dictionary1= ibm_db.fetch_both(stmt)
      print(expense)
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          print(x["EXPENSEAMOUNT"])
          total =total+ int(x["EXPENSEAMOUNT"])
          if x["CATEGORY"] == "food":
              t_food=t_food+int(x["EXPENSEAMOUNT"])
            
          elif x["CATEGORY"] == "entertainment":
              t_entertainment  += int(x["EXPENSEAMOUNT"])
        
          elif x["CATEGORY"] == "business":
              t_business  +=int(x["EXPENSEAMOUNT"])
          elif x["CATEGORY"]  == "rent":
              t_rent  += int(x["EXPENSEAMOUNT"])
           
          elif x["CATEGORY"] == "EMI":
              t_EMI  += int(x["EXPENSEAMOUNT"])
         
          elif x["CATEGORY"]  == "other":
              t_other  += int(x["EXPENSEAMOUNT"])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)
      print(texpense)
      print(expense)
       
     
      return render_template("year.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
      
@app.route("/homepage",methods=['GET','POST'])
def homepage():
  
      return render_template("homepage.html")

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')

if __name__=="__main__":
    app.run(host='127.0.0.1',port=3000,debug=True)
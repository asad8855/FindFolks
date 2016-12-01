from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

app =Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       db='findfolks',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to index
#chekc if user is in session
@app.route('/' , methods=['GET','POST'])
def index():
    #events of past 3 days
    #username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM an_event WHERE start_time >= cast((now()) as date) AND start_time < cast((now() + interval 3 day) as date)'
    cursor.execute(query)
    nextThreeDays = cursor.fetchall()
    cursor.close()
    error = None
    if(nextThreeDays):
        return render_template('index.html', posts = nextThreeDays)
    else:
        error = "Sorry, no upcoming events"
        return render_template('index.html', errorUpcoming = error)
#index execution page
@app.route('/indexfilter'  ,  methods =['GET','POST'])
def indexfilter():
    #grabs information from the forms
    interest = request.form['interest']
    cursor = conn.cursor()
    query = 'SELECT * FROM  about NATURUAL JOIN a_group WHERE category = %s'
    cursor.execute(query,(interest))
    selected_interest_table = cursor.fetchall()
    errorInterests = None
    cursor.close()
    cursor = conn.cursor()
    query = 'SELECT * FROM an_event WHERE start_time >= cast((now()) as date) AND start_time < cast((now() + interval 3 day) as date)'
    cursor.execute(query)
    nextThreeDays = cursor.fetchall()
    cursor.close()
    error = None
    if(nextThreeDays):
        if(selected_interest_table):
            return render_template('index.html' , interestTable = selected_interest_table,posts = nextThreeDays)
        else:  
            errorInterests = 'No groups currently have that interest'
            return render_template('index.html' , errorInterests = errorInterests, posts = nextThreeDays)
    else:
        error = "Sorry, no upcoming events"
        if(selected_interest_table):
            return render_template('index.html' , interestTable = selected_interest_table, errorUpcoming=error)
        else:  
            errorInterests = 'No groups currently have that interest'
            return render_template('index.html' , errorInterests = errorInterests, errorUpcoming=error)


#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for loginAuth
@app.route('/loginAuth', methods =['GET','POST'])
def loginAuth():
    #get username and password from html form
    username = request.form['username']
    password = request.form['password']

    cursor = conn.connect()
    query = 'SELECT * FROM member WHERE username = %s AND password = %s'
    cursor.execute(query,(username,password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        #create a session to hold variables that we will need throughout login session
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #return error message to html page
        error = 'Invalid login or username'
        return render_template('login.html', error = error)
        


#Define route for register
@app.route('/register' , methods=['GET', 'POST'])
def register():
        return render_template('index.html')

#register execution page
@app.route('/registerAuth' , methods=['GET', 'POST'])
def registerAuth():
    #grab information from register page
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    zipcode = request.form['zipcode']
    interest = request.interest['interest']

    cursor = conn.cursor()
    query = 'SELECT * FROM member WHERE username = %s'
    cursor.execute(query,(username))
    data = cursor.fetchone()
    error = None

    if(data):
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO member VALUES (%s,%s,%s,%s,%s,%i)'
        cursor.execute(ins , (username,password,firstname,lastname,email,zipcode))
        conn.commit()
        ins = 'INSERT INTO interested_in (username,category) VALUES (%s,%s)'
        cursor.execute(ins , (username,interest))
        cursor.close()
        return render_template('login.html')


#home page
@app.route('/home' , methods=['GET', 'POST'])
def home():
    username = session['username']
    return render_template('home.html', username = username)

#USE CASE 3
@app.route('/viewUpcomingEvents' ,  methods=['GET', 'POST'])
def viewUpcomingEvents():

    username = session['username']
    cursor = conn.cursor()
    default = 'SELECT * FROM an_event NATURAL JOIN sign_up WHERE start_time >= cast((now()) as date) AND start_time < cast((now() + interval 3 day) as date) AND username = %s'
    cursor.execute(default,(username))
    data = cursor.fetchall()
    cursor.close()
    return render_template('viewUpcomingEvents.html' , posts = data)

#USE CASE 4
@app.route('/signup' , methods=['GET', 'POST'])
def sign_up():
    username = session['username']
    cursor = conn.cursor
    #search for events of groups user belongs to
    search = 'SELECT an_event.event_id,title,description,start_time,end_time,location_name,zipcode FROM belongs_to,organize,an_event WHERE belongs_to.group_id = organize.group_id AND organize.event_id = an_event.event_id'
    cursor.execute(search)
    data = cursor.fetchall()
    return render_template('sign_up.html' , posts = data)

#sign_up execution page
@app.route('/insertSignup' , methods=['GET', 'POST'])
def insertSignup():
    username = session['username']
    cursor = conn.cursor
    event_id = request.form['event_id']
    #check if already signed up             
    check = 'SELECT * FROM sign_up WHERE username = %s AND event_id = %i'
    cursor.execute(check , (username,event_id))
    check_data = cursor.fetchone()
    error = None

    if(check_data):
        error = 'Already signed up for this event'
        return render_template('signup.html' , error = error)
    else:
        ins = 'INSERT INTO sign_up (event_id, username) VALUES(%i , %s)'
        cursor.execute(ins , (event_id, username))
        conn.commit()
        cursor.close()
        return render_template('home.html')

#USE CASE 5
@app.route('/searchByInterest' , methods=['GET', 'POST'])
def searchByInterest():
    username = session['username']
    cursor = conn.cursor
    query = 'SELECT an_event.event_id,title,description,start_time,end_time,location_name,zipcode FROM belongs_to,organize,an_event FROM an_event,organize,about,interested_in WHERE an_event.event_id = organize.event_id AND organize.group_id = about.group_id AND interested_in.category = about.category'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('searchByInterest.html' , posts = data)

 #USE CASE 6
@app.route('/create_event' , methods = ['GET', 'POST'])
def create_event():
     username = session['username'] 
     cursor = conn.cursor
     #display groups that user is part of and authorized so they can select a group nto create an event for
     query = 'SELECT * FROM a_group NATURAL JOIN belongs_to WHERE authorized = true AND username = %s'
     cursor.execute(query , (username))
     authorized_in_groups = cursor.fetchall()
     #if not athorized in any groups return to homepage
     if(not authorized_in_groups):
         return render_template('home.html')
     else:
        #need to get all these values to update the database fro new event
        #need to get group_id
        group = request.form['group_id']
        event_id = request.form['event_id']
        title = request.form['title']
        description = request.form['description']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location_name = request.form['location_name']
        zipcode = request.form['zipcode']
        location_address = request.form['location_address']
        location_description = request.form['location_description']
        location_latitude = request.form['location_latitude']
        location_longitude = request.form['location_longitude']

        ins_into_organize = 'INSERT INTO organize VALUES (%i , %i)'  
        cursor.execute(ins_into_organize , (event_id, group_id))
        conn.commit()
        ins_into_an_event = 'INSERT INTO an_event VALUES (%i,%s,%s,%s,%s,%s,i%)'
        cursor.execute(ins_into_an_event , (event_id,title,description,start_time,end_time,location_name,zipcode))
        conn.commit()
        ins_into_location = 'INSERT INTO location VALUES (%s,%i,%s,%s,%d,%d)'
        cursor.execute(ins_into_location , (location_name, zipcode, address, description, location_latitude, location_longitude))
        conn.commit()
        cursor.close()
        return render_template('create_event.html' , posts = authorized_in_groups)

#USE CASE 7
@app.route('/rate_event' ,  methods = ['GET', 'POST'])
def rate_event():
    username = session['username'] 
    cursor = conn.cursor
    #All events that user has signed up for and the event has past the end_date 
    query = 'SELECT * FROM an_event NATURAL JOIN sign_up WHERE username = %s AND end_time < cast((now()) as date)'
    cursor.execute(query , (username))
    can_rate = cursor.fetchall()
    error = None
    if(can_rate):
        #This should return an option from a list 0-5 from html page
        rating = request.form['rating']
        ins = 'INSERT INTO sign_up (rating) VALUES (%i)'
        cursor.execute(ins , (rating))
        conn.commit()
        cursor.close()
        return render_template('rate_event.html' , posts = can_rate)
    else:
        error = 'You cannot rate any events at this time'
        return render_template('rate_event.html' , error = error)

@app.route('/avg_rating')
def avg_rating():
    cursor = conn.cursor
    query = 'SELECT avg(rating) as average_ratings FROM belongs_to, organize, sign_up WHERE belongs_to.group_id = organize.group_id AND organize.event_id = sign_up.event_id AND (rating = 0 OR rating = 1 OR rating = 2 OR rating = 3 OR rating =4 OR rating = 4 OR rating = 5) GROUP BY organize.event_id'
    cursor.execute(query)
    average_rating = cursor.fetchall()
    #maybe we dont need a whole page for this query and just return to home.html --- ADD aveage_rating = average_rating
    return render_template('avg_rating.html' , posts = average_rating)

@app.route('/friends_events' , methods = ['GET', 'POST'])
def friends_events():
    return render_template('friends_events.html')



@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')



if __name__ == "__main__":
    app.run()
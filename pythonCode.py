from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

app =Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
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
    query = 'SELECT * FROM an_event WHERE start_time >= cast((now()) as date) AND start_time < cast((now() + interval 29 day) as date)'
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
    query = 'SELECT  title, start_time, end_time, description, location_name, zipcode FROM an_event NATURAL JOIN about NATURAL JOIN organize WHERE category = %s'
    cursor.execute(query,(interest))
    selected_interest_table = cursor.fetchall()
    errorInterests = None
    cursor.close()
    cursor = conn.cursor()
    query = 'SELECT * FROM an_event WHERE start_time >= cast((now()) as date) AND start_time < cast((now() + interval 29 day) as date)'
    cursor.execute(query)
    nextThreeDays = cursor.fetchall()
    cursor.close()
    error = None
    if(nextThreeDays):
        if(selected_interest_table):
            return render_template('index.html' , interestTable = selected_interest_table, posts = nextThreeDays)
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
@app.route('/login' , methods =['GET','POST'])
def login():
	return render_template('login.html')

#Define route for loginAuth
@app.route('/loginAuth', methods =['GET','POST'])
def loginAuth():
    #get username and password from html form
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM member WHERE username = %s AND password = %s'
    cursor.execute(query,(username,password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        #create a session to hold variables that we will need throughout login session
        session['username'] = username
        cursor = conn.cursor()
        query = 'SELECT * FROM an_event WHERE start_time >= cast((now()) as date) AND start_time < cast((now() + interval 29 day) as date)'
        cursor.execute(query)
        nextThreeDays = cursor.fetchall()
        cursor.close()
        if(nextThreeDays):
                return render_template('index.html' ,posts = nextThreeDays, message = username)
        else:
            error = "Sorry, no upcoming events"  
            return render_template('index.html' , errorUpcoming=error , message = username)
    else:
        #return error message to html page
        error = 'Invalid login or username'
        return render_template('login.html', error = error)
        


#Define route for register
@app.route('/register' , methods=['GET', 'POST'])
def register():
        return render_template('register.html')

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
    default = 'SELECT * FROM an_event NATURAL JOIN sign_up WHERE start_time >= cast((now()) as date) AND start_time < cast((now() + interval 29 day) as date) AND username = %s'
    cursor.execute(default,(username))
    data = cursor.fetchall()
    cursor.close()
    if(data):
        return render_template('signup.html' , posts = data)
    else: 
        error = "sorry, no upcoming events in the next 3 days."
        return render_template('signup.html' , postsError = error)

#USE CASE 4
@app.route('/signup' , methods=['GET', 'POST'])
def sign_up():
    username = session['username']
    cursor = conn.cursor()
    #search for events of groups user belongs to
    search = 'SELECT an_event.event_id,title,description,start_time,end_time,location_name,zipcode FROM belongs_to,organize,an_event WHERE belongs_to.group_id = organize.group_id AND organize.event_id = an_event.event_id'
    cursor.execute(search)
    data = cursor.fetchall()
    error = None
    if(data):
        return render_template('signup.html' , posts = data)
    else:
        error = "No events to display"
        return render_template('signup.html' , postsError = error)

#extension of signup page
@app.route('/searchByName' , methods=['GET', 'POST'])
def searchByName():
    #grab information from register page
    name = request.form['eventName']
    cursor = conn.cursor()
    search = 'SELECT an_event.event_id,title,start_time,end_time,description,location_name,zipcode FROM belongs_to,organize,an_event WHERE belongs_to.group_id = organize.group_id AND organize.event_id = an_event.event_id AND title = %s'
    cursor.execute(search , (name))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        return render_template('signup.html' , posts = data)
    else:
        cursor = conn.cursor
        #default table
        search = 'SELECT an_event.event_id,title as event_name,description,start_time,end_time,location_name,zipcode FROM belongs_to,organize,an_event WHERE belongs_to.group_id = organize.group_id AND organize.event_id = an_event.event_id'
        data = cursor.fetchall()
        cursor.close()
        error = "There are currently no events with this name"
        return render_template('signup.html' , posts = data , postsError = error)

#extension of signup page
#USE CASE 5
@app.route('/searchByInterest')
def searchByInterest():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT DISTINCT an_event.event_id,title,description,start_time,end_time,location_name,zipcode FROM belongs_to NATURAL JOIN organize NATURAL JOIN an_event NATURAL JOIN about NATURAL JOIN interested_in WHERE interested_in.username = %s '
    cursor.execute(query,(username))
    data = cursor.fetchall()
    cursor.close()
    error = None
    if(data):
        return render_template('signup.html' , posts = data)
    else:
        cursor = conn.cursor
        #default table
        search = 'SELECT an_event.event_id,title,description,start_time,end_time,location_name,zipcode FROM belongs_to,organize,an_event WHERE belongs_to.group_id = organize.group_id AND organize.event_id = an_event.event_id'
        data = cursor.fetchall()
        cursor.close()
        error = "There are currently no events that share an interest with you"
        return render_template('signup.html' , posts = data , postsError = error)
    
#extension of signup page
@app.route('/insertSignup' , methods =['GET', 'POST'])
def insertSignup():
     username = session['username']
     event_id = request.form['event_id']
     cursor = conn.cursor()
     query = 'SELECT * FROM sign_up WHERE event_id = %s AND username = %s'
     cursor.execute(query,(event_id , username))
     data = cursor.fetchone()
     error = None
     if(data):
        #default table
        search = 'SELECT an_event.event_id,title,description,start_time,end_time,location_name,zipcode FROM belongs_to,organize,an_event WHERE belongs_to.group_id = organize.group_id AND organize.event_id = an_event.event_id'
        data = cursor.fetchall()
        cursor.close()
        note = "You are already signed up for this event"
        return render_template('signup.html'  , signupMessage = note)
     else:
         #check if this user is entering an event_id that he is able to sign up for (e.g. member of the group that organizes it)
         query = 'SELECT event_id FROM belongs_to NATURAL JOIN organize WHERE  belongs_to.group_id = organize.group_id AND username = %s AND event_id = %s'
         cursor.execute(query , (username , event_id))
         data = cursor.fetchone()

         if(data):
            ins = 'INSERT INTO sign_up (event_id , username , rating) VALUES (%s,%s,6)'
            cursor.execute(ins , (event_id , username))
            cursor.close()
            note = "You are now signed up for this event!"
            return render_template('signup.html' , posts = data , signupMessage = note)
         else:
            #default table
            search = 'SELECT an_event.event_id,title,description,start_time,end_time,location_name,zipcode FROM belongs_to,organize,an_event WHERE belongs_to.group_id = organize.group_id AND organize.event_id = an_event.event_id'
            data = cursor.fetchall()
            cursor.close()
            note = "You cannot sign up for this event"
            return render_template('signup.html' ,  signupMessage = note)

 #USE CASE 6
@app.route('/create_event' , methods = ['GET', 'POST'])
def create_event():
        return render_template('create_event.html')
        

@app.route('/createEventAuth' , methods = ['GET', 'POST'])
def createEventAuth():
     username = session['username'] 
     group = request.form['group_id']
     cursor = conn.cursor()

     #checks groups that user is part of and authorized so they can select a group nto create an event for
     query = 'SELECT * FROM belongs_to WHERE authorized = true AND username = %s AND group_id = %s '
     cursor.execute(query , (username,group))
     authorized_in_groups = cursor.fetchall()
     error = None
     if(authorized_in_groups):
        #need to get group_id
        title = request.form['title']
        description = request.form['description']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location_name = request.form['location_name']
        zipcode = request.form['zipcode']
        #check that location exists
        query = 'SELECT location_name , zipcode FROM location WHERE location_name = %s AND zipcode = %s'
        cursor.execute(query , (location_name , zipcode))
        data = fetchone()
        cursor.close()
        if(data):
            cursor = conn.cursor()
            #NEED DIFFERENT QUERY TO INPUT DATE TIME
            ins_into_an_event = 'INSERT INTO an_event (title,description,start_time,end_time,location_name,zipcode) VALUES (%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(ins_into_an_event , (title,description,start_time,end_time,location_name,zipcode))
            conn.commit()
            maxID = 'SELECT MAX(event_id) FROM an_event'
            cursor.execute(maxID)
            lastID = fetchone()
            ins_into_organize = 'INSERT INTO organize VALUES (%s , %s)'  
            cursor.execute(ins_into_organize , (lastID, group_id))
            conn.commit()
            cursor.close()
            message = "You have successfully created an event!"
            return render_template('create_event.html' , error = message)
        else:
            Merror = "The location you have chosen to have this event does not exist"
            return render_template('create_event.html' , error = Merror)
     else:
        Merror = "You are not authorized to create an event for this group"
        return render_template('create_event.html' , error = Merror)



#USE CASE 7 avg ratings and rate event
@app.route('/avgRatings' ,  methods = ['GET', 'POST'])
def avgRatings():
    username = session['username'] 
    cursor = conn.cursor
    #All events that user has signed up for and the event has past the end_date DEFAULT VALUE FOR RATING IS 6 
    query = 'SELECT event_id, title , avg(rating) as average_ratings FROM an_event NATURAL JOIN sign_up WHERE username = %s AND rating != 6 AND end_time < cast((now()) as date) GROUP BY event_id'
    cursor.execute(query , (username))
    data = cursor.fetchall()
    cursor.close()
    error = None
    if(data):
        return render_template('avgRatings.html' , posts = can_rate) 
    else:
        error = "Events have yet to be rated"
        return render_template('rateEvent.html' , error = error)

#rate event execution page
@app.route('/rate_event' ,  methods = ['GET', 'POST'])
def rate_eventget():
    username = session['username']
    #This should return an option from a list 0-5 from html page
    rating = request.form['rating']
    event_id = request.form['event_id']
    cursor = conn.cursor
    query = 'SELECT * FROM an_event NATURAL JOIN sign_up WHERE username = %s AND event_id = %i'
    cursor.execute(query , (username , event_id))
    can_rate = fetchone()
    if(can_rate):
        ins = 'INSERT INTO sign_up (rating) VALUES (%i)'
        cursor.execute(ins , (rating))
        conn.commit()
        query = 'SELECT event_id, title , avg(rating) as average_ratings FROM an_event NATURAL JOIN sign_up WHERE username = %s AND rating != 6 AND end_time < cast((now()) as date) GROUP BY event_id'
        cursor.execute(query , (username))
        data = cursor.fetchall()
        cursor.close()
        return render_template('rate_event.html' , posts = data)
    else:
        error = "You cannot rate any events at this time"
        return render_template('rate_event.html' , error = error)


@app.route('/friends_events' , methods = ['GET', 'POST'])
def friends_events():
    return render_template('friends_events.html')


@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')


if __name__ == "__main__":
    app.run()
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mail import Mail, Message  # Import Mail and Message from Flask-Mail
import pymysql
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sdfsdfjij@3k4k3j4k"


# Function to format the date
def format_date(input_date):
    if isinstance(input_date, str):
        # If the input date is a string, parse it to a datetime object
        parsed_date = datetime.strptime(input_date, '%d/%m/%Y')
    elif isinstance(input_date, datetime):
        # If the input date is already a datetime object, convert it to a string
        parsed_date = input_date
    else:
        raise ValueError("Invalid input date type. Should be either str or datetime.datetime.")

    # Format the datetime object as "27 December, 2024"
    formatted_date = parsed_date.strftime('%d %B, %Y')

    return formatted_date


# Database configuration
db_config = {
    'host': 'sql5.freesqldatabase.com',
    'user': 'sql5699648',
    'password': '29By8tqFV7',
    'database': 'sql5699648',
    'cursorclass': pymysql.cursors.DictCursor
}

# Load configuration from JSON file
with open('config.json') as config_file:
    config = json.load(config_file)


# # Get database configuration from JSON
# db_config = config.get('db_config', {})


# Function to create a database connection
def create_connection():
    return pymysql.connect(**db_config)


# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ankit.developer2004@gmail.com'  # your Gmail email
app.config['MAIL_PASSWORD'] = 'rwmwsyplgggtfjyg'  # your Gmail password

mail = Mail(app)


@app.route("/")
def index():
    connection = create_connection()
    try:
        no_of_post = config['website']['no_of_post']
        with connection.cursor() as cursor:
            # Fetch all posts from the 'posts' table
            cursor.execute(f'SELECT * FROM posts ORDER BY sno DESC LIMIT {no_of_post} ')
            posts = cursor.fetchall()

    finally:
        connection.close()
    return render_template('index.html', posts=posts, config=config, format_date=format_date)


@app.route("/about")
def about():
    return render_template('about.html', config=config)


@app.route('/sample_post/<slug>', methods=['GET'])
def sample_post(slug):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch the post with the specified slug from the 'posts' table
            cursor.execute('SELECT * FROM posts WHERE slug=%s', (slug,))
            post = cursor.fetchone()

    finally:
        connection.close()
    return render_template('sample_post.html', post=post, config=config, format_date=format_date)


@app.route("/post")
def post():
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch all posts from the 'posts' table
            cursor.execute('SELECT * FROM posts ORDER BY sno DESC ')
            posts = cursor.fetchall()

    finally:
        connection.close()
    return render_template('post.html', posts=posts, config=config, format_date=format_date)


@app.route("/contact")
def contact():
    return render_template('contact.html', config=config)


@app.route("/contact", methods=['GET', 'POST'])
def submit():
    # Get data from the form
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    message = request.form['message']

    # Insert data into the database
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO login (name, email, phone, message) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, email, phone, message))
        connection.commit()
    finally:
        connection.close()
        flash('Message Sent Successfully!', 'success')
        # Send email
        send_email(name, email, phone, message)

    return render_template('contact.html', config=config)


# Function to send email
def send_email(name, email, phone, message):
    msg = Message('Form Submission',
                  sender='ankit.developer2004@gmail.com',
                  recipients=['ankit.developer2004@gmail.com'])  # recipient email

    msg.body = f'New Record Filled,\n Name : {name}\nEmail : {email}\nPhone : {phone}\nMessage : {message}'
    mail.send(msg)


# admin login page
@app.route("/manage_post", methods=['GET', 'POST'])
def admin_login():
    if "user" in session and session['user'] == config['meta_data']['admin_user']:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')

        if "user" in session and session['user'] == config['meta_data']['admin_user']:
            return redirect(url_for('dashboard'))

        else:
            if (username == config['meta_data']['admin_user'] and password == config['meta_data']['admin_password']):
                session['user'] = username
                return redirect(url_for('dashboard'))

            elif (username != config['meta_data']['admin_user'] and password != config['meta_data']['admin_password']):
                error = 'Invalid Username or Password. Please try again.'

            elif (username != config['meta_data']['admin_user']):
                error = 'Invalid Password. Please try again.'

            else:
                error = 'Invalid Password. Please try again.'

    return render_template('admin_login.html', config=config, error=error)


# dashboard page to edit post
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    user = session.get('user')
    connection = create_connection()
    if user:
        try:
            with connection.cursor() as cursor:
                # Fetch all posts from the 'posts' table
                cursor.execute('SELECT * FROM posts ')
                posts = cursor.fetchall()

        finally:
            connection.close()
        return render_template('dashboard.html', posts=posts, config=config, format_date=format_date)
    else:
        return redirect(url_for('admin_login'))


# edit post on dashboard
@app.route("/dashboard/edit/<sno>", methods=['GET', 'POST'])
def edit_post(sno):
    if "user" in session and session['user'] == config['meta_data']['admin_user']:
        # Insert data into the database
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM posts WHERE sno=%s', (sno,))
                posts = cursor.fetchone()
        finally:
            connection.close()

        if request.method == "POST":
            title = request.form.get('title')
            slug = request.form.get('slug')
            image_url = request.form.get('image_url')
            content = request.form.get('content')
            date = datetime.now()
            # Insert data into the database
            connection = create_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE posts SET title=%s, slug=%s, image_url=%s, content=%s, date=%s WHERE sno=%s',
                                   (title, slug, image_url, content, date, sno))
                connection.commit()
                return redirect(url_for('dashboard'))
            finally:
                connection.close()
    else:
        return redirect(url_for('admin_login'))

    return render_template('edit.html', posts=posts, config=config)


# Route to delete a blog post
@app.route("/dashboard/delete_post/<sno>", methods=['GET', 'POST'])
def delete_post(sno):
    if "user" in session and session['user'] == config['meta_data']['admin_user']:
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                # Delete the post from the 'posts' table
                cursor.execute('DELETE FROM posts WHERE sno=%s', (sno,))
                connection.commit()
        finally:
            connection.close()

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('admin_login'))


# Route to add a new blog post
@app.route('/dashboard/add_post', methods=['GET', 'POST'])
def add_post():
    connection = create_connection()

    if "user" in session and session['user'] == config['meta_data']['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            slug = request.form.get('slug')
            image_url = request.form.get('image_url')
            content = request.form.get('content')
            date = datetime.now()

            try:
                with connection.cursor() as cursor:
                    # Insert a new post into the 'posts' table
                    cursor.execute('INSERT INTO posts (title, slug, image_url, content, date) VALUES (%s, %s, %s, %s, %s)', (title, slug, image_url, content, date))
                    connection.commit()
            finally:
                connection.close()

            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('admin_login'))

    return render_template('add_post.html',config=config)


# Logout
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('admin_login'))
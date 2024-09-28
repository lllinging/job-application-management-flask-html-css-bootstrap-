from flask import Flask, render_template, request, redirect, url_for, g, flash, session
from flask_sqlalchemy import SQLAlchemy
# from flask_login import login_required
import secrets
from sqlalchemy import or_



from flask_migrate import Migrate

app = Flask(__name__)

#mysql host
HOSTNAME = "127.0.0.1"
#th port mysql is running on, and default is 3306
PORT = 3306
#username that you use to connect to mysql
USERNAME = "root"
#password that you use to connect to mysql
PASSWORD = "mysql"
#name of the database you created in mysql
DATABASE = "applyjobs"
user_name = ""


app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"

#set database info in app.config
# then create a db object using SQLAlchemy(app) 
# SQLAlchemy will automatically read the database connection information in app.config
db = SQLAlchemy(app)

app.secret_key = 'tricodexinfo5002'

migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login/submit', methods=['POST'])
def user_login():
    if request.method == 'POST':
        email_address = request.form['email_address']
        password = request.form['password']
        user = User.query.filter_by(email_address=email_address).one()
        global user_name
        user_name = user.first_name
        # session['user_id'] = user.id
        if password == user.password:
            return redirect('/view')
        else:
            return "the password or email address is not correct! please input the correct password."

@app.before_request
def load_user():
    global user_name
    g.user = user_name

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register/submit', methods=['POST'])
def user_register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_address = request.form['email_address']
        password = request.form['password']
        new_user = User(first_name=first_name, last_name=last_name, email_address=email_address,
                                         password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login', success=1))

class JobApplication(db.Model):
    __tablename__ = "JobApplication"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/add')
def index():

    return render_template('add.html')

@app.route('/add/submit', methods=['POST'])
def add_job_submit():
    print(request.form)
    if request.method == 'POST':
        title = request.form['title']
        company_name = request.form['company_name']
        location = request.form['location']
        contact = request.form['contact']
        link = request.form['link']
        status = request.form['status']

        new_application = JobApplication(title=title, company_name=company_name, location=location, contact=contact,
                                         link=link, status=status)
        db.session.add(new_application)
        db.session.commit()

        return redirect('/view')

@app.route('/view')
def view():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    applications = JobApplication.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('view.html', applications=applications)

@app.route('/edit_jobs')
def edit():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    applications = JobApplication.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("edit_jobs.html", applications=applications)

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = JobApplication.query.get(job_id)
    if request.method == 'POST':
        #handle form submission, update the information in the database
        job.title = request.form["title"]
        job.company_name = request.form['company_name']
        job.location = request.form["location"]
        job.contact = request.form["contact"]
        job.link = request.form['link']
        job.status = request.form['status']

        db.session.commit()
        return redirect('/view')

    return render_template('edit.html', job=job)

@app.route('/edit_job/submit')
def edit_job_submit():
    return redirect('/view')

@app.route('/delete')
def delete():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    applications = JobApplication.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("delete.html", applications=applications)

@app.route('/delete_job/<int:job_id>')
def delete_job(job_id):
    application = JobApplication.query.get(job_id)
    db.session.delete(application)
    db.session.commit()
    return redirect('/view')

@app.route('/search')
def search():
    # get data
    keyword = request.args.get('keyword')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    results = JobApplication.query.filter(or_(JobApplication.title.contains(keyword), JobApplication.company_name.contains(keyword),
                                JobApplication.location.contains(keyword), JobApplication.status.contains(keyword))).paginate(page=page, per_page=per_page, error_out=False)
    if results:
        return render_template('search_results.html', search_results=results, keyword=keyword)
    else:
        return 'Not Found'

@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
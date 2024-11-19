'''from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#create a flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask123'

#create form class
class NamerForm(FlaskForm):
    name = StringField("Ur name? :)", validators = [DataRequired()])
    submit = SubmitField("Submit")


#create a route decorator
@app.route('/')

#def index():
#   return <h1> Hello world!<h1>

def index():
    first_name = "John"
    stuff = "Namskara"
    fav_pizza = ["cheese", "pepperoni"]
    return render_template("index.html", first_name = first_name, stuff = stuff, fav_pizza = fav_pizza)

@app.route('/user/<name>')

def user(name):
    return render_template("user.html",user_name = name)

# cretae custon error pages

#invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/name', methods =['GET','POST'])
def name():
    name = None
    form = NamerForm()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted :)")

    return render_template("name.html",
                           name = name,
                           form = form)

@app.route('/tenant')
def tenant():
    return render_template('tenant.html')  # Create tenant.html in templates

@app.route('/employee')
def employee():
    return render_template('employee.html')  # Create employee.html in templates

@app.route('/owner')
def owner():
    return render_template('owner.html')  # Create owner.html in templates

'''

'''from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql123@localhost/db_project'
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

# Form for user ID input
class UserIDForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user', methods=['GET', 'POST'])
def user():
    form = UserIDForm()  # Initialize your form
    if form.validate_on_submit():
        user_id = form.user_id.data
        flash(f'User ID {user_id} submitted successfully!', 'success')
        # Render the same user.html with a success message
        return render_template('user.html', form=form)  # Keep the same page
    return render_template('user.html', form=form)  # Initial page load

if __name__ == '__main__':
    app.run(debug=True)'''

'''from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql123@localhost/db_project'
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

db = SQLAlchemy(app)

# Define Models
class Owner(db.Model):
    owner_id = db.Column(db.String(50), primary_key=True)
    owner_name = db.Column(db.String(255), nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)
    owner_pass = db.Column(db.String(255), nullable=False)  # Store hashed passwords

class Tenant(db.Model):
    tenant_id = db.Column(db.String(50), primary_key=True)
    ten_name = db.Column(db.String(255), nullable=False)
    ten_pass = db.Column(db.String(255), nullable=False)
    rental_agreement_status = db.Column(db.String(50), nullable=False, default="renewed")
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)  # Foreign key to Room


class Employee(db.Model):
    emp_id = db.Column(db.String(50), primary_key=True)
    emp_name = db.Column(db.String(255), nullable=False)
    emp_type = db.Column(db.Enum('block_admin', 'staff'), nullable=False)
    emp_pass = db.Column(db.String(255), nullable=False)  # Store hashed password
    block_no = db.Column(db.Integer, nullable=False)

    # Unique constraint to ensure only one block_admin per block
    __table_args__ = (db.UniqueConstraint('block_no', 'emp_type', name='unique_block_admin_per_block'),)

# Create tables
with app.app_context():
    db.create_all()

# Forms for Login Only
class OwnerLoginForm(FlaskForm):
    owner_id = IntegerField('Owner ID', validators=[DataRequired()])
    owner_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TenantLoginForm(FlaskForm):
    tenant_id = IntegerField('Tenant ID', validators=[DataRequired()])
    ten_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EmployeeLoginForm(FlaskForm):
    emp_id = IntegerField('Employee ID', validators=[DataRequired()])
    emp_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class Room(db.Model):
    room_no = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('1BHK', '2BHK', '3BHK'), nullable=False)
    block_no = db.Column(db.Integer, nullable=False)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.owner_id'), nullable=False)

    # Relationship with Tenant
    tenants = db.relationship('Tenant', backref='room', lazy=True)





# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Owner Login Route
@app.route('/owner/login', methods=['GET', 'POST'])
def owner_login():
    form = OwnerLoginForm()
    if form.validate_on_submit():
        owner = Owner.query.filter_by(owner_id=form.owner_id.data).first()
        if owner and check_password_hash(owner.owner_pass, form.owner_pass.data):
            flash(f'Welcome, {owner.owner_name}!', 'success')
            return redirect(url_for('owner_dashboard', owner_id=owner.owner_id))
        flash('Invalid Owner ID or Password. Please try again.', 'danger')
    return render_template('ownerLogin.html', form=form)

@app.route('/owner/<int:owner_id>')
def owner_dashboard(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    rooms = Room.query.filter_by(owner_id=owner_id).all()
    tenants = Tenant.query.join(Room, Tenant.room_no == Room.room_no).filter(Room.owner_id == owner_id).all()

    return render_template(
        'owner.html',
        owner_name=owner.owner_name,
        rooms=rooms,
        tenants=tenants
    )



# Tenant Login Route
@app.route('/tenant/login', methods=['GET', 'POST'])
def tenant_login():
    form = TenantLoginForm()
    if form.validate_on_submit():
        tenant = Tenant.query.filter_by(tenant_id=form.tenant_id.data).first()
        if tenant and check_password_hash(tenant.ten_pass, form.ten_pass.data):
            flash(f'Welcome, {tenant.ten_name}!', 'success')
            return redirect(url_for('tenant_dashboard', tenant_id=tenant.tenant_id))
        flash('Invalid Tenant ID or Password. Please try again.', 'danger')
    return render_template('tenantLogin.html', form=form)

@app.route('/tenant/<int:tenant_id>')
def tenant_dashboard(tenant_id):
    return f"Dashboard for tenant {tenant_id}"

# Employee Login Route
@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    form = EmployeeLoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(emp_id=form.emp_id.data).first()
        if employee and check_password_hash(employee.emp_pass, form.emp_pass.data):
            flash(f'Welcome, {employee.emp_name}!', 'success')
            return redirect(url_for('employee_dashboard', emp_id=employee.emp_id))
        flash('Invalid Employee ID or Password. Please try again.', 'danger')
    return render_template('employeeLogin.html', form=form)

@app.route('/employee/<int:emp_id>')
def employee_dashboard(emp_id):
    return f"Dashboard for employee {emp_id}"

if __name__ == '__main__':
    app.run(debug=True)'''

'''from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql123@localhost/db_project'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

# Models
class Owner(db.Model):
    owner_id = db.Column(db.String(50), primary_key=True)
    owner_name = db.Column(db.String(255), nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)
    owner_pass = db.Column(db.String(255), nullable=False)

class Employee(db.Model):
    emp_id = db.Column(db.String(50), primary_key=True)
    emp_name = db.Column(db.String(255), nullable=False)
    emp_type = db.Column(db.Enum('block_admin', 'staff'), nullable=False)
    emp_pass = db.Column(db.String(255), nullable=False)
    block_no = db.Column(db.Integer, nullable=False)

class Block(db.Model):
    block_no = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), db.ForeignKey('employee.emp_id'), nullable=True)

class Room(db.Model):
    room_no = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('1BHK', '2BHK', '3BHK'), nullable=False)
    block_no = db.Column(db.Integer, db.ForeignKey('block.block_no'), nullable=False)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    owner_id = db.Column(db.String(50), db.ForeignKey('owner.owner_id'), nullable=False)

class Tenant(db.Model):
    tenant_id = db.Column(db.String(50), primary_key=True)
    ten_name = db.Column(db.String(255), nullable=False)
    ten_pass = db.Column(db.String(255), nullable=False)
    rental_agreement_status = db.Column(db.String(50), nullable=False, default="renewed")
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)

class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenant.tenant_id'), nullable=False)
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

# Forms
class OwnerLoginForm(FlaskForm):
    owner_id = StringField('Owner ID', validators=[DataRequired()])
    owner_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TenantLoginForm(FlaskForm):
    tenant_id = StringField('Tenant ID', validators=[DataRequired()])
    ten_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EmployeeLoginForm(FlaskForm):
    emp_id = StringField('Employee ID', validators=[DataRequired()])
    emp_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Routes
@app.route('/owner/login', methods=['GET', 'POST'])
def owner_login():
    form = OwnerLoginForm()
    if form.validate_on_submit():
        owner = Owner.query.filter_by(owner_id=form.owner_id.data).first()
        if owner and check_password_hash(owner.owner_pass, form.owner_pass.data):
            flash(f'Welcome, {owner.owner_name}!', 'success')
            return redirect(url_for('owner_dashboard', owner_id=owner.owner_id))
        flash('Invalid Owner ID or Password. Please try again.', 'danger')
    return render_template('ownerLogin.html', form=form)

@app.route('/owner/<string:owner_id>')
def owner_dashboard(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    rooms = Room.query.filter_by(owner_id=owner_id).all()
    tenants = Tenant.query.join(Room, Tenant.room_no == Room.room_no).filter(Room.owner_id == owner_id).all()

    return render_template(
        'owner.html',
        owner_name=owner.owner_name,
        rooms=rooms,
        tenants=tenants
    )

if __name__ == '__main__':
    app.run(debug=True)'''

from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from flask import request
from datetime import datetime, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql123@localhost/db_project3'
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define Models
class Owner(db.Model):
    owner_id = db.Column(db.String(50), primary_key=True)
    owner_name = db.Column(db.String(255), nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)
    owner_pass = db.Column(db.String(255), nullable=False)  # Store hashed passwords

class Tenant(db.Model):
    tenant_id = db.Column(db.String(50), primary_key=True)
    ten_name = db.Column(db.String(255), nullable=False)
    ten_pass = db.Column(db.String(255), nullable=False)
    rental_agreement_status = db.Column(db.String(50), nullable=False, default="renewed")
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)
    agreement_expiration_date = db.Column(db.Date, nullable=True)  # Optional expiration date
    
    # Relationship to Payment
    payments = db.relationship('Payment', backref='tenant_payments', lazy=True)


class Employee(db.Model):
    emp_id = db.Column(db.String(50), primary_key=True)
    emp_name = db.Column(db.String(255), nullable=False)
    emp_type = db.Column(db.Enum('block_admin', 'staff'), nullable=False)
    emp_pass = db.Column(db.String(255), nullable=False)  # Store hashed password
    block_no = db.Column(db.Integer, nullable=False)

    # Unique constraint to ensure only one block_admin per block
    __table_args__ = (db.UniqueConstraint('block_no', 'emp_type', name='unique_block_admin_per_block'),)

class Room(db.Model):
    room_no = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('1BHK', '2BHK', '3BHK'), nullable=False)
    block_no = db.Column(db.Integer, db.ForeignKey('block.block_no'), nullable=False)  # Foreign key to Block
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    owner_id = db.Column(db.String(50), db.ForeignKey('owner.owner_id'), nullable=False)

    # Relationship with Tenant
    tenants = db.relationship('Tenant', backref='room', lazy=True)


class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenant.tenant_id'), nullable=False)
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(
        db.Enum('paid', 'pending'), 
        nullable=False
    )  # Removed default value


class Complaint(db.Model):
    complaint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    details = db.Column(db.String(255), nullable=False)  # Store complaint details
    block_no = db.Column(db.Integer, db.ForeignKey('block.block_no'), nullable=False)  # Link to block
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)  # Link to room
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenant.tenant_id'), nullable=False)  # Link to tenant
    complaint_status = db.Column(db.Enum('pending', 'resolved'), default='pending', nullable=False)



class Block(db.Model):
    block_no = db.Column(db.Integer, primary_key=True)  # Primary key for the block number
    emp_id = db.Column(db.String(50), db.ForeignKey('employee.emp_id'), nullable=True)  # Foreign key to Employee for block admin
    
    # Relationship to rooms in the block
    rooms = db.relationship('Room', backref='block', lazy=True)
    
    # Relationship to complaints if associated with a block
    complaints = db.relationship('Complaint', backref='block', lazy=True)



# Create tables
with app.app_context():
    db.create_all()

# Forms for Login Only
class OwnerLoginForm(FlaskForm):
    owner_id = StringField('Owner ID', validators=[DataRequired()])
    owner_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TenantLoginForm(FlaskForm):
    tenant_id = StringField('Tenant ID', validators=[DataRequired()])
    ten_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EmployeeLoginForm(FlaskForm):
    emp_id = StringField('Employee ID', validators=[DataRequired()])
    emp_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Owner Login Route
@app.route('/owner/login', methods=['GET', 'POST'])
def owner_login():
    form = OwnerLoginForm()
    if form.validate_on_submit():
        owner = Owner.query.filter_by(owner_id=form.owner_id.data).first()
        # Directly compare passwords if they are not hashed
        if owner and owner.owner_pass == form.owner_pass.data:
            flash(f'Welcome, {owner.owner_name}!', 'success')
            # Redirect to the 'owner' route with owner_id as a parameter
            return redirect(url_for('owner', owner_id=owner.owner_id))
        else:
            flash('Invalid Owner ID or Password. Please try again.', 'danger')
    return render_template('ownerLogin.html', form=form)

# Owner Dashboard Route
@app.route('/owner/<string:owner_id>')
def owner(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    rooms = Room.query.filter_by(owner_id=owner_id).all()

    # Query to get tenants with room and payment information
    tenants = db.session.query(
        Tenant,
        Room,
        Payment.payment_status
    ).join(Room, Tenant.room_no == Room.room_no)\
     .outerjoin(Payment, Tenant.tenant_id == Payment.tenant_id)\
     .filter(Room.owner_id == owner_id)\
     .all()

    # Aggregate functions to count total tenants and rooms
    total_rooms = Room.query.filter_by(owner_id=owner_id).count()
    total_tenants = Tenant.query.join(Room).filter(Room.owner_id == owner_id).count()

    return render_template(
        'owner.html',
        owner_name=owner.owner_name,
        rooms=rooms,
        tenants=tenants,
        total_rooms=total_rooms,
        total_tenants=total_tenants
    )





# Tenant Login Route
@app.route('/tenant/login', methods=['GET', 'POST'])
def tenant_login():
    form = TenantLoginForm()
    print("Tenant login form accessed")  # Debug statement
    if form.validate_on_submit():
        tenant = Tenant.query.filter_by(tenant_id=form.tenant_id.data).first()
        if tenant:
            # Temporarily bypass hashing for debugging purposes
            if tenant.ten_pass == form.ten_pass.data:
                flash(f'Welcome, {tenant.ten_name}!', 'success')
                return redirect(url_for('tenant_dashboard', tenant_id=tenant.tenant_id))
            else:
                print("Invalid password")  # Debug statement
                flash('Invalid Tenant ID or Password. Please try again.', 'danger')
        else:
            print("Tenant not found")  # Debug statement
            flash('Invalid Tenant ID or Password. Please try again.', 'danger')
    else:
        print(f"Form did not validate. Errors: {form.errors}")  # Debug statement

    return render_template('tenantLogin.html', form=form)




# Tenant Dashboard Route
@app.route('/tenant/<string:tenant_id>')
def tenant_dashboard(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    room = Room.query.get(tenant.room_no)
    owner = Owner.query.get(room.owner_id) if room else None
    
    # Get the latest payment entry for the tenant
    payment = Payment.query.filter_by(tenant_id=tenant.tenant_id).order_by(Payment.payment_date.desc()).first()
    
    return render_template(
        'tenant.html',
        tenant=tenant,
        room=room,
        owner=owner,
        payment=payment
    )



# Employee Login Route
@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    form = EmployeeLoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(emp_id=form.emp_id.data).first()
        if employee and employee.emp_pass == form.emp_pass.data:  # Compare directly since we are not using hashing
            flash(f'Welcome, {employee.emp_name}!', 'success')
            return redirect(url_for('employee_dashboard', emp_id=employee.emp_id))
        else:
            flash('Invalid Employee ID or Password. Please try again.', 'danger')
    return render_template('employeeLogin.html', form=form)

# Employee Dashboard Route
@app.route('/employee/<string:emp_id>')
def employee_dashboard(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    block = Block.query.filter_by(block_no=employee.block_no).first()  # Get block details

    # Get complaints associated with the block
    complaints = Complaint.query.filter_by(block_no=employee.block_no).all()  # Make sure 'Complaint' model exists

    # If the employee is staff, get the block admin for that block
    block_admin = None
    if employee.emp_type == 'staff':
        block_admin = Employee.query.filter_by(block_no=employee.block_no, emp_type='block_admin').first()

    return render_template(
        'employee.html',
        employee=employee,
        block=block,
        complaints=complaints,
        block_admin=block_admin
    )

@app.route('/tenant/<string:tenant_id>/raise_complaint', methods=['GET', 'POST'])
def raise_complaint(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    if request.method == 'POST':
        complaint_text = request.form.get('complaint_text')
        if complaint_text:
            new_complaint = Complaint(
                details=complaint_text,
                block_no=tenant.room.block_no,
                room_no=tenant.room_no,
                tenant_id=tenant.tenant_id,
                complaint_status='pending'
            )
            db.session.add(new_complaint)
            db.session.commit()
            flash('Complaint raised successfully.', 'success')
            return redirect(url_for('tenant_dashboard', tenant_id=tenant_id))
    return render_template('raise_complaint.html', tenant=tenant)

# Route to view complaints for a tenant
@app.route('/tenant/<string:tenant_id>/view_complaints')
def view_complaints(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    complaints = Complaint.query.filter_by(tenant_id=tenant_id).all()
    return render_template('view_complaints.html', tenant=tenant, complaints=complaints)

# Route to view active complaints for the employee's block
@app.route('/employee/<string:emp_id>/active_complaints')
def active_complaints(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    active_complaints = Complaint.query.filter_by(block_no=employee.block_no, complaint_status='pending').all()
    return render_template('active_complaints.html', employee=employee, complaints=active_complaints)

# Route to view resolved (past) complaints for the employee's block
@app.route('/employee/<string:emp_id>/past_complaints')
def past_complaints(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    resolved_complaints = Complaint.query.filter_by(block_no=employee.block_no, complaint_status='resolved').all()
    return render_template('past_complaints.html', employee=employee, complaints=resolved_complaints)

# Route to resolve a complaint
@app.route('/employee/<string:emp_id>/resolve_complaint/<int:complaint_id>', methods=['POST'])
def resolve_complaint(emp_id, complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.complaint_status == 'pending':
        complaint.complaint_status = 'resolved'
        db.session.commit()
        flash('Complaint resolved successfully.', 'success')
    return redirect(url_for('active_complaints', emp_id=emp_id))

@app.route('/tenant/<string:tenant_id>/renew', methods=['POST'])
def renew_agreement(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # Update the expiration date by adding 365 days from today
    tenant.agreement_expiration_date = datetime.today().date() + timedelta(days=365)
    
    # Change rental status back to "renewed"
    tenant.rental_agreement_status = "renewed"
    
    # Commit the changes to the database
    db.session.commit()
    
    flash('Agreement renewed successfully. Please proceed with payment.', 'success')
    return redirect(url_for('tenant_dashboard', tenant_id=tenant_id))


@app.route('/tenant/<string:tenant_id>/make_payment/<float:amount>', methods=['POST'])
def make_payment(tenant_id, amount):
    payment = Payment.query.filter_by(tenant_id=tenant_id, payment_status='pending').first()
    if payment:
        payment.payment_status = 'paid'
        db.session.commit()
        flash('Payment completed successfully!', 'success')
    return redirect(url_for('tenant_dashboard', tenant_id=tenant_id))

if __name__ == '__main__':
    app.run(debug=True)


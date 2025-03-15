from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    listings = db.relationship('Listing', backref='seller', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def unread_message_count(self):
        return self.received_messages.filter_by(read=False).count()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    listings = db.relationship('Listing', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    listing_type = db.Column(db.String(10), nullable=False)  # 'buy', 'sell', 'rent'
    image_filename = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    messages = db.relationship('Message', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Listing {self.title}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    read = db.Column(db.Boolean, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    
    def __repr__(self):
        return f'<Message {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor to make categories available to all templates
@app.context_processor
def inject_categories():
    categories = Category.query.all()
    return dict(categories=categories)

# Routes
@app.route('/')
def home():
    categories = Category.query.all()
    recent_listings = Listing.query.filter_by(is_active=True).order_by(Listing.date_posted.desc()).limit(6).all()
    return render_template('index.html', categories=categories, recent_listings=recent_listings)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([email, username, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        # Validate college email
        if not email.endswith('.edu'):
            flash('Please use a valid college email address (.edu)', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('register.html')
        
        try:
            user = User(email=email, username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        remember = 'remember' in request.form

        user = User.query.filter(func.lower(User.email) == email).first()

        if not user:
            flash('No account found with that email.', 'danger')
            return render_template('login.html')

        if not user.check_password(password):
            flash('Invalid password.', 'danger')
            return render_template('login.html')

        login_user(user, remember=remember)
        app.logger.info('User logged in: %s', user.username)
        flash('Logged in successfully.', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    listings = Listing.query.filter_by(category_id=category_id, is_active=True).order_by(Listing.date_posted.desc()).all()
    return render_template('category.html', category=category, listings=listings)

@app.route('/listing/<int:listing_id>')
def listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('listing.html', listing=listing)

@app.route('/create-listing', methods=['GET', 'POST'])
@login_required
def create_listing():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        listing_type = request.form.get('listing_type')
        category_id = int(request.form.get('category_id'))
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
        
        listing = Listing(
            title=title,
            description=description,
            price=price,
            listing_type=listing_type,
            image_filename=image_filename,
            user_id=current_user.id,
            category_id=category_id
        )
        
        db.session.add(listing)
        db.session.commit()
        
        flash('Your listing has been created!', 'success')
        return redirect(url_for('listing', listing_id=listing.id))
    
    return render_template('create_listing.html', categories=categories)

@app.route('/my-listings')
@login_required
def my_listings():
    listings = Listing.query.filter_by(user_id=current_user.id).order_by(Listing.date_posted.desc()).all()
    return render_template('my_listings.html', listings=listings)

@app.route('/edit-listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    
    if listing.user_id != current_user.id:
        abort(403)
    
    categories = Category.query.all()
    
    if request.method == 'POST':
        listing.title = request.form.get('title')
        listing.description = request.form.get('description')
        listing.price = float(request.form.get('price'))
        listing.listing_type = request.form.get('listing_type')
        listing.category_id = int(request.form.get('category_id'))
        
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                # Delete old image if exists
                if listing.image_filename:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], listing.image_filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
                listing.image_filename = image_filename
        
        db.session.commit()
        
        flash('Your listing has been updated!', 'success')
        return redirect(url_for('listing', listing_id=listing.id))
    
    return render_template('edit_listing.html', listing=listing, categories=categories)

@app.route('/delete-listing/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    
    if listing.user_id != current_user.id:
        abort(403)
    
    # Delete image if exists
    if listing.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], listing.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(listing)
    db.session.commit()
    
    flash('Your listing has been deleted!', 'success')
    return redirect(url_for('my_listings'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    category_id = request.args.get('category_id')
    listing_type = request.args.get('listing_type')
    
    listings_query = Listing.query.filter_by(is_active=True)
    
    if query:
        listings_query = listings_query.filter(
            (Listing.title.contains(query)) | 
            (Listing.description.contains(query))
        )
    
    if category_id and category_id != 'all':
        listings_query = listings_query.filter_by(category_id=int(category_id))
    
    if listing_type and listing_type != 'all':
        listings_query = listings_query.filter_by(listing_type=listing_type)
    
    listings = listings_query.order_by(Listing.date_posted.desc()).all()
    categories = Category.query.all()
    
    return render_template('search.html', 
                          listings=listings, 
                          categories=categories, 
                          query=query, 
                          selected_category=category_id, 
                          selected_type=listing_type)

# Initialize database with categories
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add categories if they don't exist
        categories = [
            'Textbooks',
            'Electronics',
            'Furniture',
            'Clothing',
            'Mess Meals',
            'Food',
            'Services',
            'Housing/Rentals',
            'Transportation',
            'Other'
        ]
        
        for cat_name in categories:
            if not Category.query.filter_by(name=cat_name).first():
                category = Category(name=cat_name)
                db.session.add(category)
        
        db.session.commit()

# Initialize the database
init_db()

# Messaging routes
@app.route('/send_message/<int:listing_id>/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(listing_id, recipient_id):
    listing = Listing.query.get_or_404(listing_id)
    recipient = User.query.get_or_404(recipient_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(
                content=content,
                sender_id=current_user.id,
                recipient_id=recipient_id,
                listing_id=listing_id
            )
            db.session.add(message)
            db.session.commit()
            flash('Message sent successfully!', 'success')
            return redirect(url_for('listing', listing_id=listing_id))
    
    return render_template('send_message.html', listing=listing, recipient=recipient)

@app.route('/messages')
@login_required
def messages():
    # Get all unique conversations (grouped by the other user and listing)
    sent_messages = db.session.query(Message.recipient_id, Message.listing_id).filter(Message.sender_id == current_user.id).distinct().all()
    received_messages = db.session.query(Message.sender_id, Message.listing_id).filter(Message.recipient_id == current_user.id).distinct().all()
    
    conversations = []
    
    # Process sent messages
    for recipient_id, listing_id in sent_messages:
        recipient = User.query.get(recipient_id)
        listing = Listing.query.get(listing_id)
        if recipient and listing:
            # Get the latest message in this conversation
            latest_message = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) |
                ((Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id))
            ).filter(Message.listing_id == listing_id).order_by(Message.timestamp.desc()).first()
            
            # Check if this conversation is already in our list
            if not any(c['user'].id == recipient.id and c['listing'].id == listing.id for c in conversations):
                conversations.append({
                    'user': recipient,
                    'listing': listing,
                    'latest_message': latest_message,
                    'unread_count': 0  # We sent these, so they're not unread for us
                })
    
    # Process received messages
    for sender_id, listing_id in received_messages:
        sender = User.query.get(sender_id)
        listing = Listing.query.get(listing_id)
        if sender and listing:
            # Get the latest message in this conversation
            latest_message = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.recipient_id == sender_id)) |
                ((Message.sender_id == sender_id) & (Message.recipient_id == current_user.id))
            ).filter(Message.listing_id == listing_id).order_by(Message.timestamp.desc()).first()
            
            # Count unread messages
            unread_count = Message.query.filter_by(
                sender_id=sender_id,
                recipient_id=current_user.id,
                listing_id=listing_id,
                read=False
            ).count()
            
            # Check if this conversation is already in our list
            existing_conv = next((c for c in conversations if c['user'].id == sender.id and c['listing'].id == listing.id), None)
            if existing_conv:
                existing_conv['unread_count'] = unread_count
            else:
                conversations.append({
                    'user': sender,
                    'listing': listing,
                    'latest_message': latest_message,
                    'unread_count': unread_count
                })
    
    # Sort conversations by the timestamp of the latest message, newest first
    conversations.sort(key=lambda x: x['latest_message'].timestamp if x['latest_message'] else datetime.min, reverse=True)
    
    return render_template('messages.html', conversations=conversations)

@app.route('/conversation/<int:user_id>/<int:listing_id>')
@login_required
def conversation(user_id, listing_id):
    other_user = User.query.get_or_404(user_id)
    listing = Listing.query.get_or_404(listing_id)
    
    # Get all messages between the current user and the other user for this listing
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).filter(Message.listing_id == listing_id).order_by(Message.timestamp.asc()).all()
    
    # Mark unread messages as read
    unread_messages = Message.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        listing_id=listing_id,
        read=False
    ).all()
    
    for message in unread_messages:
        message.read = True
    
    db.session.commit()
    
    return render_template('conversation.html', messages=messages, other_user=other_user, listing=listing)

if __name__ == '__main__':
    app.run(debug=True)

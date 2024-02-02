from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'

with app.app_context():
    db = SQLAlchemy(app)

# Models
class User(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), nullable=False, unique=True)
    MembershipDate = db.Column(db.Date, nullable=False)
    borrowed_books = db.relationship('BorrowedBooks', backref='user', lazy=True)

class Book(db.Model):
    BookID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    ISBN = db.Column(db.String(13), nullable=False, unique=True)
    PublishedDate = db.Column(db.Date, nullable=False)
    Genre = db.Column(db.String(50), nullable=False)
    book_details = db.relationship('BookDetails', backref='book', uselist=False, lazy=True)
    borrowed_books = db.relationship('BorrowedBooks', backref='book', lazy=True)

class BookDetails(db.Model):
    DetailsID = db.Column(db.Integer, primary_key=True)
    BookID = db.Column(db.Integer, db.ForeignKey('book.BookID'), nullable=False, unique=True)
    NumberOfPages = db.Column(db.Integer, nullable=False)
    Publisher = db.Column(db.String(255), nullable=False)
    Language = db.Column(db.String(50), nullable=False)

class BorrowedBooks(db.Model):
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), primary_key=True)
    BookID = db.Column(db.Integer, db.ForeignKey('book.BookID'), primary_key=True)
    BorrowDate = db.Column(db.Date, nullable=False)
    ReturnDate = db.Column(db.Date, nullable=True)

# User APIs
#Required Parameters: ["Name", "Email", "MembershipDate"]
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        # Convert the string to a Python date object
        membership_date = datetime.strptime(data.get('MembershipDate'), '%Y-%m-%d').date()
        
        new_user = User(Name=data.get('Name'), Email=data.get('Email'), MembershipDate=membership_date)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def list_all_users():
    try:
        users = User.query.all()
        users_data = [{'UserID': user.UserID, 'Name': user.Name, 'Email': user.Email, 'MembershipDate': user.MembershipDate} for user in users]
        return jsonify({'users': users_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        user = User.query.get_or_404(user_id)
        user_data = {'UserID': user.UserID, 'Name': user.Name, 'Email': user.Email, 'MembershipDate': user.MembershipDate}
        return jsonify({'user': user_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Book APIs
#Required Parameters: ["Title", "ISBN", "PublishedDate", "Genre"]
@app.route('/books', methods=['POST'])
def add_new_book():
    try:
        data = request.json
        published_date = datetime.strptime(data.get('PublishedDate'), '%Y-%m-%d').date()
        new_book = Book(Title=data['Title'], ISBN=data['ISBN'], PublishedDate=published_date, Genre=data['Genre'])
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/books', methods=['GET'])
def list_all_books():
    try:
        books = Book.query.all()
        books_data = [{'BookID': book.BookID, 'Title': book.Title, 'ISBN': book.ISBN, 'PublishedDate': book.PublishedDate, 'Genre': book.Genre} for book in books]
        return jsonify({'books': books_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        book_data = {'BookID': book.BookID, 'Title': book.Title, 'ISBN': book.ISBN, 'PublishedDate': book.PublishedDate, 'Genre': book.Genre}
        return jsonify({'book': book_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#Required Parameters: ["BookID", "NumberOfPages", "Publisher", "Language"]
@app.route('/books/<int:book_id>/details', methods=['POST', 'PUT'])
def assign_update_book_details(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        data = request.json

        if 'NumberOfPages' in data:
            book_details = BookDetails.query.filter_by(BookID=book_id).first()
            if book_details:
                book_details.NumberOfPages = data['NumberOfPages']
                book_details.Publisher = data['Publisher']
                book_details.Language = data['Language']
            else:
                new_book_details = BookDetails(BookID=book_id, NumberOfPages=data['NumberOfPages'], Publisher=data['Publisher'], Language=data['Language'])
                db.session.add(new_book_details)

            db.session.commit()
            return jsonify({'message': 'Book details updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# BorrowedBooks APIs
#Required Parameters: ["UserID", "BookID", "BorrowDate"]
@app.route('/borrow', methods=['POST'])
def borrow_book():
    try:
        data = request.json
        borrow_date = datetime.strptime(data.get('BorrowDate'), '%Y-%m-%d').date()
        new_borrowed_book = BorrowedBooks(UserID=data['UserID'], BookID=data['BookID'], BorrowDate=borrow_date)
        db.session.add(new_borrowed_book)
        db.session.commit()
        return jsonify({'message': 'Book borrowed successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Required Parameters: ["ReturnDate"]
@app.route('/return/<int:user_id>/<int:book_id>', methods=['PUT'])
def return_book(user_id, book_id):
    try:
        borrowed_book = BorrowedBooks.query.filter_by(UserID=user_id, BookID=book_id, ReturnDate=None).first_or_404()
        borrowed_book.ReturnDate = datetime.strptime(request.json.get('ReturnDate'), '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({'message': 'Book returned successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/borrowed-books', methods=['GET'])
def list_all_borrowed_books():
    try: 
        borrowed_books = BorrowedBooks.query.filter_by(ReturnDate=None).all()
        borrowed_books_data = [{'UserID': book.UserID, 'BookID': book.BookID, 'BorrowDate': book.BorrowDate} for book in borrowed_books]
        return jsonify({'borrowed_books': borrowed_books_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

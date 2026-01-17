"""
Part 4: REST API with Flask
===========================
Build a JSON API for database operations (used by frontend apps, mobile apps, etc.)

What You'll Learn:
- REST API concepts (GET, POST, PUT, DELETE)
- JSON responses with jsonify
- API error handling
- Status codes
- Testing APIs with curl or Postman

Prerequisites: Complete part-3 (SQLAlchemy)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =============================================================================
# MODELS
# =============================================================================

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    city = db.Column(db.String(100))

    # Relationship: One author → many books
    books = db.relationship('Book', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'city': self.city
        }


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
#   author = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author.name if self.author else None,
            'author_id': self.author_id,
            'year': self.year,
            'isbn': self.isbn,
            'created_at': self.created_at.isoformat()
        }
        


# =============================================================================
# REST API ROUTES
# =============================================================================

# GET /api/books - Get all books
@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    print("books fetched")
    print(type(books))
    return jsonify({  # Return JSON response
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]  # List comprehension to convert all
    })


# GET /api/books/<id> - Get single book
@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({
            'success': False,
            'error': 'Book not found'
        }), 404  # Return 404 status code

    return jsonify({
        'success': True,
        'book': book.to_dict()
    })


# POST /api/books - Create new book
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()  # Get JSON data from request body

    # Validation
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if not data.get('title') or not data.get('author_id'):
        return jsonify({'success': False, 'error': 'Title and Author ID are required'}), 400
    
    #check if author exists
    author_id = db.session.get(Author, data['author_id'])
    if not author_id:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    # Check for duplicate ISBN
    if data.get('isbn'):
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({'success': False, 'error': 'ISBN already exists'}), 400

    # Create book
    new_book = Book(
        title=data['title'],
        author_id=data['author_id'],
        year=data.get('year'),
        isbn=data.get('isbn')
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book created successfully',
        'book': new_book.to_dict()
    }), 201  # 201 = Created


# PUT /api/books/<id> - Update book
@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
    if 'author_id' in data:
       author = db.session.get(Author, data['author_id'])
    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404
    book.author_id = data['author_id']

    if 'year' in data:
        book.year = data['year']
    if 'isbn' in data:
        book.isbn = data['isbn']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book updated successfully',
        'book': book.to_dict()
    })


# DELETE /api/books/<id> - Delete book
@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book deleted successfully'
    })


# =============================================================================
# BONUS: Search and Filter
# =============================================================================

# GET /api/books/search?q=python&author=john
@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = Book.query

    # Filter by title (partial match)
    title = request.args.get('q')  # Query parameter: ?q=python
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))  # Case-insensitive LIKE

    # Filter by author
    author = request.args.get('author')
    if author:
     query = query.join(Author).filter(
        Author.name.like(f'%{author}%')
    )


    # Filter by year
    year = request.args.get('year')
    if year:
        query = query.filter_by(year=int(year))

    books = query.all()

    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })


#====================================AUTHOR API ROUTES=====================================

#create author

@app.route('/api/authors', methods=['POST'])
def create_author():
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'success': False, 'error': 'Name is required'}), 400

    author = Author(
        name=data['name'],
        bio=data.get('bio'),
        city=data.get('city')
    )

    db.session.add(author)
    db.session.commit()

    return jsonify({'success': True, 'author': author.to_dict()}), 201


#get all authors

@app.route('/api/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()

    return jsonify({
        'success': True,
        'count': len(authors),
        'authors': [a.to_dict() for a in authors]
    })


#ge single author

@app.route('/api/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = db.session.get(Author, id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    return jsonify({'success': True, 'author': author.to_dict()})


#update author

@app.route('/api/authors/<int:id>', methods=['PUT'])
def update_author(id):
    author = db.session.get(Author, id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    data = request.get_json()

    if 'name' in data:
        author.name = data['name']
    if 'bio' in data:
        author.bio = data['bio']
    if 'city' in data:
        author.city = data['city']

    db.session.commit()

    return jsonify({'success': True, 'author': author.to_dict()})


#delete author

@app.route('/api/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = db.session.get(Author, id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    if author.books:
        return jsonify({
            'success': False,
            'error': 'Cannot delete author with existing books'
        }), 400

    db.session.delete(author)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Author deleted'})


# =============================================================================
# SIMPLE WEB PAGE FOR TESTING
# =============================================================================

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Part 4 - REST API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            h1 { color: #e94560; }
            .endpoint { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e94560; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
            .get { background: #27ae60; }
            .post { background: #f39c12; }
            .put { background: #3498db; }
            .delete { background: #e74c3c; }
            code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
            pre { background: #0f3460; padding: 15px; border-radius: 8px; overflow-x: auto; }
            a { color: #e94560; }
        </style>
    </head>
    <body>
        <h1>Part 4: REST API Demo</h1>
        <p>This is a JSON API - use curl, Postman, or JavaScript fetch() to test!</p>

        <h2>API Endpoints:</h2>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books</code> - Get all books
            <br><a href="/api/books" target="_blank">Try it →</a>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books/&lt;id&gt;</code> - Get single book
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/books</code> - Create new book
        </div>

        <div class="endpoint">
            <span class="method put">PUT</span>
            <code>/api/books/&lt;id&gt;</code> - Update book
        </div>

        <div class="endpoint">
            <span class="method delete">DELETE</span>
            <code>/api/books/&lt;id&gt;</code> - Delete book
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books/search?q=&lt;title&gt;&author=&lt;name&gt;</code> - Search books
        </div>

        <h2>Test with curl:</h2>
        <pre>
# Get all books
curl http://localhost:5000/api/books

# Create a book
curl -X POST http://localhost:5000/api/books \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Flask Web Development", "author": "Miguel Grinberg", "year": 2018}'

# Update a book
curl -X PUT http://localhost:5000/api/books/1 \\
  -H "Content-Type: application/json" \\
  -d '{"year": 2023}'

# Delete a book
curl -X DELETE http://localhost:5000/api/books/1
        </pre>
    </body>
    </html>
    '''


# =============================================================================
# INITIALIZE DATABASE WITH SAMPLE DATA
# =============================================================================

def init_db():
    with app.app_context():
        db.create_all()

        if Author.query.count() == 0:
            authors = [
                Author(name='Eric Matthes', city='USA'),
                Author(name='Miguel Grinberg', city='USA'),
                Author(name='Robert C. Martin', city='USA'),
         ]   
            db.session.add_all(authors)
            db.session.commit()

        if Book.query.count() == 0:
            books = [
                Book(title='Python Crash Course', author_id=authors[0].id, year=2019, isbn='978-1593279288'),
                Book(title='Flask Web Development', author_id=authors[1].id, year=2018, isbn='978-1491991732'),
                Book(title='Clean Code', author_id=authors[2].id, year=2008, isbn='978-0132350884'),
            ]
            db.session.add_all(books)
            db.session.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# REST API CONCEPTS:
# =============================================================================
#
# HTTP Method | CRUD      | Typical Use
# ------------|-----------|---------------------------
# GET         | Read      | Retrieve data
# POST        | Create    | Create new resource
# PUT         | Update    | Update entire resource
# PATCH       | Update    | Update partial resource
# DELETE      | Delete    | Remove resource
#
# =============================================================================
# HTTP STATUS CODES:
# =============================================================================
#
# Code | Meaning
# -----|------------------
# 200  | OK (Success)
# 201  | Created
# 400  | Bad Request (client error)
# 404  | Not Found
# 500  | Internal Server Error
#
# =============================================================================
# KEY FUNCTIONS:
# =============================================================================
#
# jsonify()           - Convert Python dict to JSON response
# request.get_json()  - Get JSON data from request body
# request.args.get()  - Get query parameters (?key=value)
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Create new class say "Author" with fields id, name, bio, city with its table. 
# Write all CRUD api routes for it similar to Book class.
# Additionally try to link Book and Author class such that each book has one author and one author can have multiple books.

# 1. Create 2 simple frontend using JavaScript fetch()
# This is a bigger exercise. Create a frontend in HTML and JS that uses all api routes and displays data dynamically, along with create/edit/delete functionality.
# Since the API is through n through accessible on the computer/server, you don't need to use render_template from flask, instead, 
# you can directly use ipaddress:portnumber/apiroute from any where. So your HTML JS code can be anywhere on computer (not necessarily in flask)  

# 3. Add pagination: `/api/books?page=1&per_page=10` 
# Hint - the sqlalchemy provides paginate method. 
# OPTIONAL - For ease of understanding, create a new api say /api/books-with-pagination which takes page number and number of books per page

# 4. Add sorting: `/api/books?sort=title&order=desc`
# OPTIONAL - For ease of understanding, create a new api say /api/books-with-sorting
#
# =============================================================================
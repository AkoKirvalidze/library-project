import os
from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, validators, FileField, IntegerField, ValidationError

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteka.db'
app.config["SECRET_KEY"] = 'supersecretkey'
app.config["UPLOAD_FOLDER"] = 'static/files'
db = SQLAlchemy(app)


class Form(FlaskForm):
    name = StringField('name', validators=[validators.DataRequired()])
    description = StringField('description', validators=[validators.DataRequired()])
    author = StringField('author', validators=[validators.DataRequired()])
    genre = StringField('genre', validators=[validators.DataRequired()])
    ISBN = IntegerField('ISBN', validators=[validators.DataRequired()])

    def validate_ISBN(self, field):
        isbn = field.data
        existing_book = Book.query.filter_by(ISBN=isbn).first()
        if existing_book:
            raise ValidationError('This ISBN already exists. Please enter a different ISBN.')

    available = StringField('available', validators=[validators.DataRequired()])
    image = FileField('image', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')


class Book(db.Model):
    __tablename__ = 'library'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String)
    author = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    ISBN = db.Column(db.Integer)
    available = db.Column(db.String(10))
    filename = db.Column(db.String())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'genre': self.genre,
            'ISBN': self.ISBN,
            'available': self.available,
            'filename': self.filename
        }


@app.route('/')
def get_books():
    books = [book.to_dict() for book in Book.query.all()]
    categories = []
    for i in books:
        categories.append(i["genre"])
    categories = list(set(categories))
    return render_template('showbook.html', categories=categories, books=books)


@app.route('/library', methods=['POST', 'GET'])
def create_book():
    form = Form()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        author = form.author.data
        genre = form.genre.data
        ISBN = form.ISBN.data
        available = form.available.data
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                secure_filename(image.filename)))
        book = Book(name=name, description=description, author=author, genre=genre, ISBN=ISBN, available=available,
                    filename=filename)
        db.session.add(book)
        db.session.commit()
        return redirect('/')
    return render_template('addbook.html', form=form)


@app.route('/library/update/<int:id>', methods=['POST', 'GET'])
def update_book(id):
    book = Book.query.get(id)
    form = Form()
    if form.validate_on_submit():
        book.name = form.name.data
        book.description = form.description.data
        book.author = form.author.data
        book.genre = form.genre.data
        book.ISBN = form.ISBN.data
        book.available = form.available.data
        book.image = form.image.data
        book.filename = secure_filename(book.image.filename)
        book.image.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                     secure_filename(book.image.filename)))
        db.session.commit()
        return redirect('/')
    return render_template('update.html', form=form, id=id)


@app.route('/category/<string:genre>')
def category(genre):
    books = [book.to_dict() for book in Book.query.filter(Book.genre == genre).all()]
    books2 = [book.to_dict() for book in Book.query.all()]
    return render_template('category.html', books=books, books2=books2)


@app.route('/library/delete/<int:id>')
def delete_student(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return redirect('/')


@app.route('/book/<int:id>')
def book_info(id):
    book = Book.query.get(id).to_dict()
    books2 = [book.to_dict() for book in Book.query.filter(Book.genre == book['genre']).all()]
    return render_template('bookinfo.html', book=book, books2=books2)


@app.route('/about')
def about():
    return render_template("about.html")


with app.app_context():
    db.create_all()
    # app.run()

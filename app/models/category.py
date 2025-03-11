from datetime import datetime
from app.models import db

# Association table for shelf-category many-to-many relationship
shelf_categories = db.Table('shelf_categories',
    db.Column('shelf_id', db.Integer, db.ForeignKey('shelves.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Products are referenced via backref in Product model
    # Shelves are referenced via backref in Shelf model
    
    def __repr__(self):
        return f'<Category {self.name}>'
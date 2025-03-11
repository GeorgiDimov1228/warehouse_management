from datetime import datetime
from app.models import db
from app.models.category import shelf_categories

class Cabinet(db.Model):
    __tablename__ = 'cabinets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category_mode = db.Column(db.String(20), default='single')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shelves = db.relationship('Shelf', backref='cabinet', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Cabinet {self.name}>'

class Shelf(db.Model):
    __tablename__ = 'shelves'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    allows_multiple_categories = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    cabinet_id = db.Column(db.Integer, db.ForeignKey('cabinets.id'))
    
    # Relationships
    categories = db.relationship('Category', secondary=shelf_categories, lazy='subquery',
                               backref=db.backref('shelves', lazy=True))
    transactions = db.relationship('Transaction', backref='shelf', lazy=True)
    rfid_trackings = db.relationship('RFIDTracking', backref='shelf', lazy=True)
    
    def __repr__(self):
        return f'<Shelf {self.name} in Cabinet {self.cabinet_id}>'
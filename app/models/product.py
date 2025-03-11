from datetime import datetime
from app.models import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    rfid_tag = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Relationships
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    transactions = db.relationship('Transaction', backref='product', lazy=True)
    rfid_trackings = db.relationship('RFIDTracking', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
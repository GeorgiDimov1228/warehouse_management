from datetime import datetime
from app.models import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelves.id'))
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.transaction_type} at {self.timestamp}>'
    
    @staticmethod
    def add_transaction(user_id, product_id, quantity, transaction_type, shelf_id=None):
        """Helper method to add a new transaction"""
        transaction = Transaction(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            transaction_type=transaction_type,
            shelf_id=shelf_id
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

class RFIDTracking(db.Model):
    __tablename__ = 'rfid_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    rfid_tag = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    
    # Foreign keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelves.id'))
    
    def __repr__(self):
        return f'<RFIDTracking {self.id}: {self.status} at {self.timestamp}>'
    
    @staticmethod
    def track_rfid(rfid_tag, product_id, shelf_id, status):
        """Helper method to track RFID movement"""
        tracking = RFIDTracking(
            rfid_tag=rfid_tag,
            product_id=product_id,
            shelf_id=shelf_id,
            status=status
        )
        db.session.add(tracking)
        db.session.commit()
        return tracking

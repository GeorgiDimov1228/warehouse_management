import logging
from flask import current_app
import requests
import json
import uuid
import time
from app.models import db
from app.models.product import Product
from app.models.transaction import RFIDTracking


class RFIDPrinterException(Exception):
    """Exception raised for RFID printer errors"""
    pass


class RFIDReaderException(Exception):
    """Exception raised for RFID reader errors"""
    pass


def encode_rfid_tag(product_id, rfid_tag=None):
    """
    Encode a new RFID tag for a product using connected RFID printer
    
    Args:
        product_id: The ID of the product to encode
        rfid_tag: Optional specific RFID tag to use (if None, generates new)
        
    Returns:
        The encoded RFID tag
    """
    try:
        # Get product details
        product = Product.query.get_or_404(product_id)
        
        # If no RFID tag specified, generate a new one
        if not rfid_tag:
            rfid_tag = generate_unique_rfid_tag()
        
        # Connect to the RFID printer using API details from config
        printer_api_url = current_app.config.get('RFID_PRINTER_API_URL')
        api_key = current_app.config.get('RFID_PRINTER_API_KEY')
        
        # Prepare data for the printer
        printer_data = {
            'product_id': product.id,
            'product_name': product.name,
            'barcode': product.barcode,
            'rfid_tag': rfid_tag,
            'category_id': product.category_id
        }
        
        # Send print job to the printer
        response = requests.post(
            printer_api_url,
            json=printer_data,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise RFIDPrinterException(f"Printer API returned status {response.status_code}: {response.text}")
        
        # Update product's RFID tag in database
        product.rfid_tag = rfid_tag
        db.session.commit()
        
        logging.info(f"RFID tag {rfid_tag} encoded and printed for product {product_id}")
        return rfid_tag
        
    except requests.RequestException as e:
        logging.error(f"RFID printer communication error: {str(e)}")
        raise RFIDPrinterException(f"Failed to communicate with RFID printer: {str(e)}")
    except Exception as e:
        logging.error(f"RFID encoding error: {str(e)}")
        db.session.rollback()
        raise RFIDPrinterException(f"Failed to encode RFID tag: {str(e)}")


def generate_unique_rfid_tag():
    """
    Generate a unique RFID tag that doesn't exist in the system
    
    Returns:
        A unique RFID tag string
    """
    # Create a format based on time and random component
    tag_prefix = current_app.config.get('RFID_TAG_PREFIX', 'RF')
    tag_base = f"{tag_prefix}{int(time.time())}"
    random_component = str(uuid.uuid4()).split('-')[0]
    new_tag = f"{tag_base}-{random_component}"
    
    # Verify it doesn't already exist
    while Product.query.filter_by(rfid_tag=new_tag).first():
        random_component = str(uuid.uuid4()).split('-')[0]
        new_tag = f"{tag_base}-{random_component}"
    
    return new_tag


def process_rfid_scan(reader_id, rfid_tags):
    """
    Process RFID scan data from a reader
    
    Args:
        reader_id: ID of the RFID reader
        rfid_tags: List of RFID tags scanned
        
    Returns:
        Dictionary with processing results
    """
    results = {
        'processed': 0,
        'unknown_tags': [],
        'items': []
    }
    
    for tag in rfid_tags:
        # Look up the product by RFID tag
        product = Product.query.filter_by(rfid_tag=tag).first()
        
        if not product:
            results['unknown_tags'].append(tag)
            continue
        
        # Log that this product was scanned
        tracking = RFIDTracking(
            rfid_tag=tag,
            product_id=product.id,
            status='scanned'
        )
        db.session.add(tracking)
        
        results['processed'] += 1
        results['items'].append({
            'product_id': product.id,
            'name': product.name,
            'category_id': product.category_id
        })
    
    db.session.commit()
    logging.info(f"Processed RFID scan from reader {reader_id}: {len(rfid_tags)} tags, {results['processed']} items identified")
    
    return results


def simulate_rfid_scan(reader_id, rfid_tags):
    """
    Simulate an RFID scan for testing purposes
    
    Args:
        reader_id: ID of the simulated RFID reader
        rfid_tags: List of RFID tags to simulate scanning
    
    Returns:
        Results from processing the scan
    """
    logging.info(f"Simulating RFID scan from reader {reader_id} with {len(rfid_tags)} tags")
    return process_rfid_scan(reader_id, rfid_tags)
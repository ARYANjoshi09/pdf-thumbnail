import json
import boto3
import io
from datetime import datetime
import base64

# Try pdf2image, fallback to basic approach if it fails
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

from PIL import Image, ImageDraw, ImageFont

def lambda_handler(event, context):
    """
    Ultra-simple AWS Lambda function for PDF thumbnails
    Works on Windows and AWS Lambda without compilation issues
    """
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Parse and validate input
        s3_bucket = event.get('s3_bucket')
        s3_key = event.get('s3_key')
        document_id = event.get('document_id', 'unknown')
        
        if not s3_bucket or not s3_key:
            return error_response(400, 'Missing s3_bucket or s3_key')
        
        print(f"Processing PDF: {s3_bucket}/{s3_key}")
        
        # Download PDF from S3
        try:
            response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            pdf_data = response['Body'].read()
            print(f"Downloaded PDF: {len(pdf_data)} bytes")
        except Exception as e:
            return error_response(404, f'Failed to download PDF: {str(e)}')
        
        # Generate thumbnail
        thumbnail_bytes = None
        method = 'placeholder'
        
        # Try pdf2image if available
        if PDF2IMAGE_AVAILABLE:
            try:
                print("Trying pdf2image conversion...")
                images = convert_from_bytes(pdf_data, first_page=1, last_page=1, dpi=150)
                if images:
                    thumbnail_bytes = process_pdf_image(images[0])
                    method = 'pdf2image'
                    print(f"pdf2image success: {len(thumbnail_bytes)} bytes")
            except Exception as e:
                print(f"pdf2image failed: {str(e)}")
        
        # Generate placeholder if pdf2image failed or unavailable
        if not thumbnail_bytes:
            print("Generating placeholder thumbnail...")
            thumbnail_bytes = generate_simple_placeholder(document_id)
            method = 'placeholder'
        
        # Upload to S3
        thumbnail_url = upload_thumbnail(s3_client, s3_bucket, document_id, thumbnail_bytes)
        
        # Return success
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'document_id': document_id,
                'thumbnail_url': thumbnail_url,
                'thumbnail_size': len(thumbnail_bytes),
                'method': method
            })
        }
        
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        return error_response(500, f'Lambda function error: {str(e)}')

def process_pdf_image(pil_image):
    """Process PIL image into thumbnail"""
    pil_image.thumbnail((400, 500), Image.Resampling.LANCZOS)
    final_image = Image.new('RGB', (400, 500), 'white')
    paste_x = (400 - pil_image.width) // 2
    paste_y = (500 - pil_image.height) // 2
    final_image.paste(pil_image, (paste_x, paste_y))
    
    img_buffer = io.BytesIO()
    final_image.save(img_buffer, format='JPEG', quality=85, optimize=True)
    return img_buffer.getvalue()

def generate_simple_placeholder(document_id):
    """Generate a simple placeholder thumbnail"""
    img = Image.new('RGB', (400, 500), '#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Draw border and PDF icon
    draw.rectangle([10, 10, 390, 490], outline='#dee2e6', width=2)
    draw.rectangle([175, 200, 225, 280], fill='#dc3545', outline='#c82333', width=2)
    
    # Add text with default font
    try:
        font = ImageFont.load_default()
        draw.text((200, 240), "PDF", fill='white', font=font, anchor='mm')
        display_name = document_id[:20] + "..." if len(document_id) > 20 else document_id
        draw.text((200, 320), display_name, fill='#495057', font=font, anchor='mm')
        draw.text((200, 340), "PDF Document", fill='#6c757d', font=font, anchor='mm')
    except:
        pass  # Skip text if font fails
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=85)
    return img_buffer.getvalue()

def upload_thumbnail(s3_client, s3_bucket, document_id, thumbnail_bytes):
    """Upload thumbnail to S3"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S-%fZ')
    thumbnail_key = f"thumbnails/{document_id}/{timestamp}-thumbnail.jpg"
    
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=thumbnail_key,
        Body=thumbnail_bytes,
        ContentType='image/jpeg',
        CacheControl='public, max-age=31536000'
    )
    
    return f"https://mediacdn.strater.in/{thumbnail_key}"

def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'body': json.dumps({
            'success': False,
            'error': message
        })
    }

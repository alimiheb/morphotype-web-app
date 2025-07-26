import os
import logging
from flask import Flask, request, render_template, jsonify, url_for, redirect, flash
from werkzeug.utils import secure_filename
from morphotype_analyzer import MorphotypeAnalyzer
import psutil
import time
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_resource_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        
        start_mem = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent(interval=None)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_mem = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = psutil.cpu_percent(interval=None)
        
        logger.info(f"⏱️ Execution time: {end_time - start_time:.3f} seconds")
        logger.info(f"🧠 RAM used: {end_mem - start_mem:.3f} MB")
        logger.info(f"⚙️ CPU usage: {end_cpu - start_cpu:.2f}%")
        
        return result
    return wrapper

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the morphotype analyzer
analyzer = MorphotypeAnalyzer()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@monitor_resource_usage
def upload_file():
    """Handle file upload and morphotype analysis"""
    try:
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get form data including new fields
            age = int(request.form.get('age', 25))
            gender = request.form.get('gender', 'unknown')
            activity_level = request.form.get('activity_level', 'moderate')
            goal = request.form.get('goal', 'muscle_gain')
            preferences = request.form.get('preferences', '')
            height = float(request.form.get('height', 0))  # New field
            weight = float(request.form.get('weight', 0))  # New field
            
            # Validate new fields
            if height <= 0 or weight <= 0:
                flash('Please provide valid height and weight values.', 'error')
                return redirect(url_for('index'))
            
            analyzer = MorphotypeAnalyzer()
            result = analyzer.analyze_image(
                filepath, 
                age=age, 
                gender=gender, 
                activity_level=activity_level, 
                goal=goal, 
                preferences=preferences,
                height=height,  # Pass height
                weight=weight   # Pass weight
            )
            
            if result['success']:
                return render_template('results.html', 
                                     result=result,
                                     image_url=url_for('static', filename=f'uploads/{filename}'))
            else:
                flash(f"Analysis failed: {result['error']}")
                return redirect(url_for('index'))
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files.')
            return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash(f'Error processing your request: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
@monitor_resource_usage
def api_analyze():
    """API endpoint for programmatic access"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get parameters from form data or JSON
        data = request.get_json() if request.is_json else request.form
        age = int(data.get('age', 25))
        gender = data.get('gender', 'unknown')
        activity_level = data.get('activity_level', 'moderate')
        goal = data.get('goal', 'muscle_gain')
        preferences = data.get('preferences', '')
        
        # Analyze the image
        result = analyzer.analyze_image(
            filepath,
            age=age,
            gender=gender,
            activity_level=activity_level,
            goal=goal,
            preferences=preferences
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"API analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Morphotype Analyzer',
        'version': '1.0.0'
    })

@app.errorhandler(413)
def too_large(e):
    flash("File is too large. Maximum size is 16MB.")
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    flash("An internal server error occurred. Please try again.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Morphotype Analyzer on port {port}")
    logger.info(f"📁 Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

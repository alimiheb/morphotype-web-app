# Morphotype Web Application

A modern web application that analyzes body morphotypes (Ectomorph, Mesomorph, Endomorph) using MediaPipe AI and provides personalized fitness and nutrition plans.

## 🚀 Features

- **AI-Powered Body Analysis**: Uses MediaPipe for accurate pose detection and body proportion analysis
- **Morphotype Classification**: Automatically determines your body type based on scientific measurements
- **Personalized Plans**: Generates custom workout routines and nutrition plans based on your morphotype
- **Modern Web Interface**: Clean, responsive design with drag-and-drop image upload
- **Real-time Results**: Instant analysis with detailed visualizations
- **Resource Monitoring**: Built-in performance tracking and optimization

## 📋 Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- Flask
- PIL (Pillow)
- NumPy
- Pandas

## 🛠️ Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd morphotype-web-app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 🎯 How to Use

1. **Upload Image**: Use a clear, full-body photo in good lighting
2. **Fill Form**: Provide your age, gender, activity level, and fitness goals
3. **Analyze**: Click "Analyze My Body Type" to process your image
4. **Get Results**: View your morphotype classification and personalized plans

## 📊 Morphotype Classification

### Ectomorph
- **Characteristics**: Lean build, narrow shoulders and hips, fast metabolism
- **Training**: Focus on mass building with compound movements
- **Nutrition**: Higher calorie intake with balanced macros

### Mesomorph  
- **Characteristics**: Naturally muscular, athletic build, balanced metabolism
- **Training**: Balanced strength and conditioning programs
- **Nutrition**: Moderate calories with emphasis on protein

### Endomorph
- **Characteristics**: Broader build, slower metabolism, tendency to store fat
- **Training**: High-intensity workouts with more cardio
- **Nutrition**: Lower carb, higher protein approach

## 🔧 Technical Details

### Core Components

- **`app.py`**: Main Flask application with routes and error handling
- **`morphotype_analyzer.py`**: Core analysis logic using MediaPipe
- **`templates/`**: HTML templates for the web interface
- **`static/`**: CSS, JavaScript, and uploaded images
- **`config.py`**: Application configuration and settings

### Analysis Process

1. **Image Preprocessing**: Remove EXIF data and convert to OpenCV format
2. **Pose Detection**: Use MediaPipe to identify body landmarks
3. **Measurements**: Calculate shoulder width, hip width, and ratios
4. **Classification**: Determine morphotype based on scientific thresholds
5. **Plan Generation**: Create personalized workout and nutrition plans

### API Endpoints

- **`GET /`**: Main upload form
- **`POST /upload`**: Process image upload and analysis
- **`POST /api/analyze`**: API endpoint for programmatic access
- **`GET /health`**: Health check endpoint

## 🎨 Features

### Web Interface
- Responsive design that works on all devices
- Drag-and-drop image upload with preview
- Real-time form validation
- Loading states and error handling
- Print-friendly results page

### Analysis Features
- MediaPipe pose detection
- 3D body measurements
- Confidence scoring
- TDEE calculation
- Morphotype-specific recommendations

### Personalization
- Age and gender considerations
- Activity level adjustments
- Goal-based plan customization
- Dietary preference accommodation

## 🚀 Deployment

### Local Development
```bash
export FLASK_ENV=development
python app.py
```

### Production (using Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Variables
- `FLASK_ENV`: Set to 'production' for production deployment
- `SECRET_KEY`: Set a secure secret key for production
- `PORT`: Port number (default: 5000)

## 📝 Notes

- **Image Quality**: Use clear, well-lit, full-body images for best results
- **Privacy**: Images are processed locally and not stored permanently
- **Accuracy**: Results are estimates based on visible body proportions
- **Medical Advice**: Consult healthcare professionals before starting new programs

## 🤝 Based on Research

This application implements morphotype classification based on:
- Somatotype theory by William Sheldon
- Modern exercise science principles
- Nutritional guidelines from sports science
- MediaPipe pose estimation technology

## 📈 Performance

The application includes built-in monitoring for:
- Memory usage tracking
- CPU utilization
- Processing time measurement
- Error logging and handling

## 🔒 Security Features

- File type validation
- File size limits (16MB max)
- CSRF protection
- Input sanitization
- Secure file handling

---

**Disclaimer**: This application provides estimates based on image analysis. Results should be used as general guidance only. Always consult with qualified healthcare and fitness professionals before making significant changes to your diet or exercise routine.

import tensorflow as tf
import numpy as np
from PIL import Image
import json
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PredictionResult
from .serializers import PredictionSerializer

# Load your trained model
MODEL_PATH = 'path/to/your/model.h5'
# model = tf.keras.models.load_model(MODEL_PATH)

def preprocess_image(image):
    """Preprocess image for VGG-19 model"""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = image.resize((224, 224))
    img_array = np.array(image)
    img_array = tf.keras.applications.vgg19.preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0)

@api_view(['GET'])
def home_page(request):
    """Web page for image upload"""
    return render(request, 'prediction/index.html')

@api_view(['POST'])
def predict_image(request):
    """API endpoint for prediction - FIXED JSON response"""
    try:
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Check if image was uploaded
        if 'image' not in request.FILES:
            if is_ajax:
                return JsonResponse({'error': 'No image file uploaded'}, status=400)
            return render(request, 'prediction/index.html', {'error': 'No image file uploaded'})
        
        image_file = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if image_file.content_type not in allowed_types:
            if is_ajax:
                return JsonResponse({'error': 'Invalid file type. Use JPG or PNG.'}, status=400)
            return render(request, 'prediction/index.html', {'error': 'Invalid file type'})
        
        # Process image
        image = Image.open(image_file)
        processed_image = preprocess_image(image)
        
        # Make prediction
        prediction = 0.5 # model.predict(processed_image)
        confidence = 0.2 # float(prediction[0][0])
        result = "Pneumonia" if confidence > 0.5 else "Normal"
        
        # Save to database
        prediction_obj = PredictionResult.objects.create(
            image=image_file,
            result=result,
            confidence=confidence
        )
        
        # Prepare response data
        response_data = {
            'success': True,
            'result': result,
            'confidence': round(confidence, 4),
            'message': 'Pneumonia detected' if result == 'Pneumonia' else 'No pneumonia detected',
            'image_url': prediction_obj.image.url
        }
        
        # Return JSON for AJAX requests, HTML for form submissions
        if is_ajax:
            return JsonResponse(response_data)
        else:
            return render(request, 'prediction/result.html', response_data)
            
    except Exception as e:
        error_msg = str(e)
        # Return proper JSON error for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': error_msg}, status=500)
        return render(request, 'prediction/index.html', {'error': error_msg})

# prediction/views.py - Add this function
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Avg, Q

@api_view(['GET'])
def prediction_history(request):
    """View prediction history with statistics"""
    # Get all predictions ordered by date
    predictions = PredictionResult.objects.all().order_by('-created_at')

    # Calculate statistics
    total_predictions = predictions.count()
    pneumonia_count = predictions.filter(result='Pneumonia').count()
    normal_count = predictions.filter(result='Normal').count()

    # Calculate average confidence
    avg_confidence = predictions.aggregate(avg_confidence=Avg('confidence'))['avg_confidence'] or 0
    accuracy = round(avg_confidence * 100, 1) if avg_confidence else 0

    # Pagination
    paginator = Paginator(predictions, 12)  # Show 12 predictions per page
    page = request.GET.get('page')

    try:
        predictions_page = paginator.page(page)
    except PageNotAnInteger:
        predictions_page = paginator.page(1)
    except EmptyPage:
        predictions_page = paginator.page(paginator.num_pages)

    # Return JSON for API calls
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        from .serializers import PredictionSerializer
        serializer = PredictionSerializer(predictions_page, many=True)
        return Response({
            'predictions': serializer.data,
            'total_predictions': total_predictions,
            'pneumonia_count': pneumonia_count,
            'normal_count': normal_count,
            'accuracy': accuracy,
            'total_pages': paginator.num_pages,
            'current_page': predictions_page.number
        })

    # Return HTML for web
    context = {
        'predictions': predictions_page,
        'total_predictions': total_predictions,
        'pneumonia_count': pneumonia_count,
        'normal_count': normal_count,
        'accuracy': accuracy,
    }

    return render(request, 'prediction/history.html', context)

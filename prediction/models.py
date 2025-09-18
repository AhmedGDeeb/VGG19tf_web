from django.db import models

class PredictionResult(models.Model):
    image = models.ImageField(upload_to='predictions/')
    result = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction {self.id} - {self.result}"

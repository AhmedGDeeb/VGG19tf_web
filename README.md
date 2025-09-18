# VGG19tf_web
A web deployment with django for VGG 19 model with transfer learning

# usage
## curl post
```bash
curl -X POST -F "image=@xray.jpg" http://localhost:8000/predict/
```

## python
```py
import requests

url = "http://localhost:8000/predict/"
files = {"image": open("xray.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```
## curl API
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"image": "base64_encoded_image"}' \
     http://localhost:8000/predict/
```


import time

from django.shortcuts import render,HttpResponse,redirect
import requests
import numpy as np
from .models import Stock
from .serializers import ImageUploadSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import os
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

search_object = None  

def home_page(request):
    if request.method =="POST":
        return redirect("output")
    return render(request,template_name="homepage.html",)

def initial_page(request):
    if request.method =="POST":
        return redirect("output")
    return render(request,template_name="index.html",)










def investment_summary_view(request):
    # Define object symbols
    global search_object
    stock_symbols = request.POST.getlist("ticker")
    time.sleep(5)
    if "smartphone" in stock_symbols :
        search_object = "smartphone"
        context = {
            "image":"static/images/image_phone.jpg"
        }
    else:
        search_object = "laptop"
        context = {
            "image": "static/images/laptop_laptop.jpg"
        }
    
    return render(request, 'output.html', context)


@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    # Initialize the serializer with the incoming data
    serializer = ImageUploadSerializer(data=request.data)

    if serializer.is_valid():
        # Get the camera index and file from the request
        camera_index = serializer.validated_data['camera_index']
        uploaded_file = serializer.validated_data['file']

        # Save the uploaded file (you can change the directory as needed)
        file_path = os.path.join('/Users/sharifovazizbek/IOT/Iot/found_images', f"Camera{camera_index}_{uploaded_file.name}")
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        return Response({"message": f"File received from Camera {camera_index} and saved to {file_path}."}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_search_object(request):
    global search_object
    if search_object:
        header = {"search_object": search_object}
        return JsonResponse(header)
    return JsonResponse({"search_object": None})


from django.shortcuts import render,redirect
import requests

from .models import Images
from .serializers import ImageUploadSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt
search_object = None  

def home_page(request):
    if request.method =="POST":
        return redirect("output")
    return render(request,template_name="homepage.html",)

def initial_page(request):
    if request.method =="POST":
        objecte = request.POST.get("object")
        requests.post("http://192.168.219.103:5000/search_object",data={"item_name":objecte})
        return redirect("output")
    return render(request,template_name="index.html",)


@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    serializer = ImageUploadSerializer(data=request.data)

    if serializer.is_valid():
        # Get the camera index and file from the request
        camera_index = serializer.validated_data['camera_index']
        uploaded_file = serializer.validated_data['files']
        Images.objects.create(image=uploaded_file,indexs=camera_index).save()
        

        return Response("",status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def render_view(request):
    if request.method == "POST":
        Images.objects.all().delete()
        return redirect("index")
    
    images = Images.objects.all()
    return render(request,template_name="output.html",context={"images":images})


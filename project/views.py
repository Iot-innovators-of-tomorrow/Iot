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
@csrf_exempt
def initial_page(request):
    if request.method =="POST":

        
        objecte = request.POST.get("object")
        header = {"Content-Type":"applicaiton/json"}
        # requests.post("http://192.168.219.106:5000/search_object/",json={"item_name":objecte},headers=header )
        return redirect("output")
    return render(request,template_name="index.html",)


@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    
    if request.data:
        message = request.POST.get("message")
        print(message,message == None)    
        camera_index = request.POST.get('camera_index')
        Images.objects.create(image=request.FILES.get("file"),indexs=camera_index).save()
        

        return Response("",status=status.HTTP_201_CREATED)
    else:

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def render_view(request):
    if request.method == "POST":
        Images.objects.all().delete()
        return redirect("index")
    
    images = Images.objects.all()
    length = len(images)
    return render(request,template_name="output.html",context={"images":images,"length":length})

def no_page_view(request):
    render(request,template_name="no_page.html")
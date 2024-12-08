from django.urls import path
from .views import initial_page,render_view,home_page, upload_image
urlpatterns = [
    path("",home_page),
    path("index/", initial_page,name="index"),
    path("pictures/", upload_image,name="pictures"),
    path("output/", render_view,name="output"),


]


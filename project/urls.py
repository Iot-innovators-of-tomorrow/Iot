from django.urls import path
from .views import initial_page,render_view,home_page, upload_image,no_page_view
urlpatterns = [
    path("",home_page,name="home_page"),
    path("index/", initial_page,name="index"),
    path("pictures/", upload_image,name="pictures"),
    path("output/", render_view,name="output"),
    path("no_page/", no_page_view,name="no_page"),


]


from django.urls import path
from .views import initial_page,investment_summary_view,home_page, upload_image
urlpatterns = [
    path("",home_page),
    path("index/", initial_page,name="index"),
    path("output/", investment_summary_view,name="output"),
    path("pictures/", upload_image,name="pictures"),

]

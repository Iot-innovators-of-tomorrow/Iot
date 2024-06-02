from django.urls import path
from .views import initial_page,investment_summary_view
urlpatterns = [
    path("",initial_page),
    path("output/", investment_summary_view,name="output"),

]

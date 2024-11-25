from django.db import models
from datetime import datetime
# Create your models here.
class Stock(models.Model):
    image = models.ImageField(upload_to="images",default=None)
    def __str__(self):
        return self.ticker

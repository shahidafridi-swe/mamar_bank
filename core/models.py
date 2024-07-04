from django.db import models

class Bank(models.Model):
    name = models.CharField(max_length=255, default='')
    is_bankrupt = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.name

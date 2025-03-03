from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TodoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_done = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    deadline = models.DateField()
    
    
    class Meta:
        db_table = "todolist"

    def __str__(self):
        return self.title
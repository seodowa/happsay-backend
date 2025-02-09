from django.test import TestCase
from .models import TodoList
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import make_aware

# Create your tests here.

class TodoListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="seodowa",
            password="test123"
        )
        self.todo = TodoList.objects.create(
            title="test todo",
            content="test todo",
            deadline=make_aware(datetime(2025, 2, 14)),
            user=self.user
        )
    

    def test_todo_creation(self):
        self.assertEqual(self.todo.user.username, "seodowa")
        self.assertEqual(self.todo.title, "test todo")
        self.assertEqual(self.todo.content, "test todo")
        self.assertEqual(self.todo.deadline.strftime("%m/%d/%Y, %H:%M:%S"), "02/14/2025, 00:00:00")


    def test_todo_update(self):
        self.todo.title = "updated test"
        self.todo.save()
        self.assertEqual(self.todo.title, "updated test")


    def test_todo_delete(self):
        self.todo.delete()
        with self.assertRaises(TodoList.DoesNotExist):
            TodoList.objects.get(user=self.user)
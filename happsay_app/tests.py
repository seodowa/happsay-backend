from django.test import TestCase
from .models import TodoList
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import make_aware
from rest_framework.test import APITestCase 

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


        
class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')


    def test_valid_login(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)  # Match your response structure


    def test_invalid_login(self):
        response = self.client.post('/login/', {'username': 'wrong', 'password': 'wrong'})
        self.assertEqual(response.status_code, 400)
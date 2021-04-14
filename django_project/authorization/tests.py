from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from authorization.models import User


class UserRegistrationTest(APITestCase):
    def setUp(self) -> None:
        self.login = 'test'
        self.password = 'test'
        self.url = reverse('user_registration')


    def test_registration(self):
        response = self.client.post(self.url, data={'login': self.login, 'password': self.password},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_existing_user(self):
        User.objects.create_user(login=self.login,
                                 password=self.password)
        response = self.client.post(self.url, data={'login': self.login, 'password': self.password},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(APITestCase):
    def setUp(self) -> None:
        self.login = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.login,
                                             self.password)

    def test_login(self):
        url = reverse('user_login')
        response = self.client.post(url, data={'login': self.login, 'password': self.password},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserInfoTest(APITestCase):
    def setUp(self) -> None:
        self.login = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.login,
                                             self.password)
        self.client.login(username=self.login,
                          password=self.password)
        self.url = reverse('user_info')

    def test_get_user_info(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'login': self.login})







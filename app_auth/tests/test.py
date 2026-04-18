from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()

class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.password_reset_url = reverse('password_reset')
        self.valid_user_data = {
            "email": "test@example.com",
            "password": "Password123!",
            "confirmed_password": "Password123!"
        }

    def test_register_happy_path(self):
        """Happy Path: Successful registration."""
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], "test@example.com")
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_register_unhappy_path_duplicate_email(self):
        """Unhappy Path: Registration with existing email."""
        User.objects.create_user(email="test@example.com", password="Password123!")
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User already exists.")

    def test_activation_happy_path(self):
        """Happy Path: Successful account activation."""
        user = User.objects.create_user(email="activate@example.com", password="Password123!", is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Account successfully activated.")
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_login_happy_path(self):
        """Happy Path: Successful login with cookies."""
        User.objects.create_user(email="login@example.com", password="Password123!", is_active=True)
        response = self.client.post(self.login_url, {"email": "login@example.com", "password": "Password123!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], "login@example.com")
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_login_unhappy_path_wrong_password(self):
        """Unhappy Path: Login fails with generic message for wrong password."""
        User.objects.create_user(email="fail@example.com", password="Password123!", is_active=True)
        response = self.client.post(self.login_url, {"email": "fail@example.com", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid credentials or inactive account.")

    def test_password_reset_initiation_generic_response(self):
        """Security: Password reset initiation always returns 200 OK (Generic Response)."""
        # Testing with non-existing email
        response = self.client.post(self.password_reset_url, {"email": "nonexistent@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "An email has been sent to reset your password.")
        
        # Testing with existing email
        User.objects.create_user(email="exists@example.com", password="Password123!")
        response = self.client.post(self.password_reset_url, {"email": "exists@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_happy_path(self):
        """Happy Path: Successful password reset with valid token."""
        user = User.objects.create_user(email="reset@example.com", password="OldPassword123!")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('password_confirm', kwargs={'uidb64': uid, 'token': token})
        payload = {"new_password": "NewPassword123!", "confirm_password": "NewPassword123!"}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPassword123!"))

    def test_logout_clears_cookies(self):
        """Happy Path: Logout clears authentication cookies."""
        user = User.objects.create_user(email="logout@example.com", password="Password123!", is_active=True)
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Logout successful!", response.data['detail'])
        # In DRF tests, deleted cookies show up with empty value and max-age=0 or similar
        self.assertEqual(response.cookies['access_token'].value, '')
        self.assertEqual(response.cookies['refresh_token'].value, '')

    def test_refresh_token_success(self):
        """Happy Path: Access token can be refreshed using the refresh cookie."""
        user = User.objects.create_user(email="refresh@example.com", password="Password123!", is_active=True)
        login_res = self.client.post(self.login_url, {"email": "refresh@example.com", "password": "Password123!"})
        refresh_cookie = login_res.cookies['refresh_token'].value
        
        self.client.cookies['refresh_token'] = refresh_cookie
        refresh_res = self.client.post(reverse('token_refresh'))
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh_res.data['detail'], "Token refreshed")
        self.assertIn('access', refresh_res.data)
        self.assertIn('access_token', refresh_res.cookies)

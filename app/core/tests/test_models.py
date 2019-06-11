from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@gmail.com', password='test123'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """Test creating a new user is successful"""
        email = "khashayar@gmail.com"
        password = "2128"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalized_right(self):
        """Testing if email is normalized correctly"""
        email = "khashayar@GMAIL.COM"
        user = get_user_model().objects.create_user(email, "khash123")

        self.assertEqual(user.email, email.lower())

    def test_validation_of_email(self):
        """Testing if email is valid"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "123")

    def test_super_user(self):
        """Testing if superuser can be created"""
        user = get_user_model().objects.create_superuser(
            "midnight_cowboy@gmail.com",
            "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test that name will return as the tag string"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

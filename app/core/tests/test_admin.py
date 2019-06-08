from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_admin = get_user_model().objects.create_superuser(
            email="admin@khashayaar.ir",
            password="admin123"
        )
        self.client.force_login(self.user_admin)
        self.user = get_user_model().objects.create_user(
            email="test@khashayaar.ir",
            password="test123",
            name="test_user0"
        )

    def test_users_listed(self):
        """Test users that are stored"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_change_page(self):
        """Test changes on users works properly"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that user add page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

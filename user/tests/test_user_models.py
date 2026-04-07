from django.test import TestCase, Client
from django.contrib.auth.hashers import check_password
from django.urls import reverse

from user.models import User


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="1qazcde3",
        )
        self.superuser = User.objects.create_superuser(
            email="superuser@test.com",
            password="2wsxvfr4",
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), "user@test.com")

    def test_email_used_as_username_field(self):
        self.assertEqual(self.user.USERNAME_FIELD, "email")

    def test_username_not_in_field_names(self):
        field_names = [field.name for field in User._meta.get_fields()]
        self.assertNotIn("username", field_names)

    def test_password_is_hashed(self):
        self.assertTrue(check_password("1qazcde3", self.user.password))

    def test_is_staff_is_superuser_false_by_default(self):
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_create_user_without_email_raises_value_error(self):
        data = {
            "email":"",
            "password":"2wsxvfr4",
        }
        with self.assertRaises(ValueError):
            User.objects.create_user(**data)

    def test_is_staff_is_superuser_true_for_superuser(self):
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    def test_forcing_is_staff_false_on_superuser_raises_value_error(self):
        data = {
            "email":"superuser2@test.com",
            "password":"2wsxvfr4",
            "is_staff":False,
        }
        with self.assertRaises(ValueError):
            User.objects.create_superuser(**data)

    def test_forcing_is_superuser_false_on_superuser_raises_value_error(self):
        data = {
            "email":"superuser2@test.com",
            "password":"2wsxvfr4",
            "is_superuser":False,
        }
        with self.assertRaises(ValueError):
            User.objects.create_superuser(**data)


class UserAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email="admin@test.com",
            password="1qazcde3",
        )
        self.client.force_login(self.admin)

    def test_admin_page_returns_200(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_username_not_in_list_display(self):
        url = reverse("admin:user_user_changelist")
        response = self.client.get(url)
        self.assertNotIn("username", response.content.decode())

    def test_username_not_in_add_fieldsets(self):
        url = reverse("admin:user_user_add")
        response = self.client.get(url)
        self.assertNotIn("username", response.content.decode())

    def test_username_not_in_fieldsets(self):
        url = reverse("admin:user_user_change", args=[self.admin.id])
        response = self.client.get(url)
        self.assertNotIn("username", response.content.decode())

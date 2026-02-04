from datetime import date, timedelta

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status

from ideas.models import Season

User = get_user_model()


class CloseSeasonTest(TestCase):

    def setUp(self):
        # ---------- API client ----------
        self.client = APIClient()

        # ---------- Director user ----------
        self.user = User.objects.create_user(
            email="director@test.com",
            password="123456"
        )

        director_group = Group.objects.create(name="incubator directors")
        self.user.groups.add(director_group)

        self.client.force_authenticate(user=self.user)

        # ---------- Season ----------
        self.season = Season.objects.create(
            name="Season 1",
            is_open=True,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        # ---------- URL ----------
        self.url = reverse(
            "admin-close-season",
            kwargs={"season_id": self.season.id}
        )

    def test_close_season_success(self):
        """
        Director can successfully close an open season
        """
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.season.refresh_from_db()
        self.assertFalse(self.season.is_open)

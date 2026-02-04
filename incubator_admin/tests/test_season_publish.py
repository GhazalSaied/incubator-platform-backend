from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status

from ideas.models import Season, IdeaForm, FormQuestion

User = get_user_model()


class SeasonPublishTests(APITestCase):

    def setUp(self):
        # ──────────────── User (Incubator Director) ────────────────
        self.user = User.objects.create_user(
            email="director@test.com",
            password="123456"
        )

        director_group = Group.objects.create(name="incubator directors")
        self.user.groups.add(director_group)

        self.client.force_authenticate(user=self.user)

        # ──────────────── Season ────────────────
        self.season = Season.objects.create(
            name="Season 1",
            start_date="2026-01-01",
            end_date="2026-03-01"
        )

        self.url = f"/admin-panel/seasons/{self.season.id}/publish/"

    # ───────────────────────────────────────────
    # ❌ Cannot publish without form
    # ───────────────────────────────────────────
    def test_cannot_publish_season_without_form(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("فورم", str(response.data))

    # ───────────────────────────────────────────
    # ❌ Cannot publish with empty form
    # ───────────────────────────────────────────
    def test_cannot_publish_season_with_empty_form(self):
        IdeaForm.objects.create(
            season=self.season,
            title="Idea Form"
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("أسئلة", str(response.data))

    # ───────────────────────────────────────────
    # ✅ Can publish with ready form
    # ───────────────────────────────────────────
    def test_can_publish_season_with_ready_form(self):
        form = IdeaForm.objects.create(
            season=self.season,
            title="Idea Form"
        )

        FormQuestion.objects.create(
            form=form,
            key="problem",
            label="ما المشكلة؟",
            type="text",
            required=True,
            order=1
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.season.refresh_from_db()
        self.assertTrue(self.season.is_open)

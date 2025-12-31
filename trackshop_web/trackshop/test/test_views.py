from django.test import TestCase
from django.urls import reverse

class TestTrackshop(TestCase):

	def test_load_index_page(self):

		response = self.client.get(reverse("TrackShop:index"))
		self.assertEqual(response.status_code, 200)
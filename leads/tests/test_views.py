# It Is Mainly to check whether the request is "OK" or "NOT"

from django.test import TestCase
from django.urls import reverse



class LandingPageTest(TestCase):

    # def test_status_code(self):
    #     # TODO some sort of test
    #     response = self.client.get(reverse("landing-page"))
    #     # print(response.content)
    #     # print(response.status_code)
    #     self.assertEqual(response.status_code, 200)

    # def test_template_name(self):
    #     # TODO some sort of test
    #     response = self.client.get(reverse("landing-page"))
    #     self.assertTemplateUsed(response, "landing.html")

    def test_get(self):
        # TODO some sort of test
        response = self.client.get(reverse("landing-page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing.html")
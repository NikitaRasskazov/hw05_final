from django.test import TestCase, Client

from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    ADDRESS_AUTHOR = '/about/author/'
    ADDRESS_TECH = '/about/tech/'
    TEMPLATE_TECH = 'about/tech.html'
    TEMPLATE_AUTHOR = 'about/author.html'

    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        addresses = (self.ADDRESS_AUTHOR, self.ADDRESS_TECH)
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_uses_correct_template(self):
        templates_url_names = {
            self.ADDRESS_TECH: self.TEMPLATE_TECH,
            self.ADDRESS_AUTHOR: self.TEMPLATE_AUTHOR
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

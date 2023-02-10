from django.test import TestCase

from http import HTTPStatus


class ViewTestClass(TestCase):
    NONEXIST_PAGE = '/nonexist-page/'
    TEMPLATE_404 = 'core/404.html'

    def test_error_page(self):
        response = self.client.get(self.NONEXIST_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, self.TEMPLATE_404)

from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

from posts.models import Post, Group, User
from posts.tests import const_value


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=const_value.USERNAME_AUTH)
        cls.another_author = User.objects.create_user(
            username=const_value.ANOTHER_AUTHOR
        )
        cls.group = Group.objects.create(
            title=const_value.GROUP_TITLE_MAIN,
            slug=const_value.GROUP_SLUG_MAIN,
            description=const_value.GROUP_DESCRIPTION_MAIN,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=const_value.POST_TEXT_MAIN,
        )
        cls.PROFILE = reverse(
            const_value.URL_PROFILE,
            args=[cls.post.author]
        )
        cls.GROUP_LIST = reverse(
            const_value.URL_GROUP_LIST,
            args=[cls.group.slug]
        )
        cls.POST_EDIT = reverse(
            const_value.URL_POST_EDIT,
            args=[cls.post.id]
        )
        cls.POST_DETAIL = reverse(
            const_value.URL_POST_DETAIL,
            args=[cls.post.id]
        )
        cls.CREATE_COMMENT = reverse(
            const_value.URL_CREATE_COMMENT,
            args=[cls.post.id]
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostURLTests.user)
        self.another_author_authorized = Client()
        self.another_author_authorized.force_login(PostURLTests.another_author)

    def test_url_exists(self):
        action = [
            (
                const_value.URL_INDEX_BASE,
                HTTPStatus.OK,
                HTTPStatus.OK,
                HTTPStatus.OK
            ),
            (
                self.GROUP_LIST,
                HTTPStatus.OK,
                HTTPStatus.OK,
                HTTPStatus.OK
            ),
            (
                self.PROFILE,
                HTTPStatus.OK,
                HTTPStatus.OK,
                HTTPStatus.OK
            ),
            (
                self.POST_DETAIL,
                HTTPStatus.OK,
                HTTPStatus.OK,
                HTTPStatus.OK
            ),
            (
                const_value.URL_POST_CREATE_BASE,
                HTTPStatus.OK,
                HTTPStatus.OK,
                HTTPStatus.FOUND
            ),
            (
                self.POST_EDIT,
                HTTPStatus.OK,
                HTTPStatus.FOUND,
                HTTPStatus.FOUND
            ),
            (
                self.CREATE_COMMENT,
                HTTPStatus.FOUND,
                HTTPStatus.FOUND,
                HTTPStatus.FOUND
            ),
            (
                const_value.URL_UNEXISTING_PAGE,
                HTTPStatus.NOT_FOUND,
                HTTPStatus.NOT_FOUND,
                HTTPStatus.NOT_FOUND
            )]
        for address, auth_cond, an_auth_cond, guest_cond in action:
            for client, cond in [
                (self.authorized_client_author, auth_cond),
                (self.another_author_authorized, an_auth_cond),
                (self.guest_client, guest_cond)
            ]:
                with self.subTest(address=address):
                    response = client.get(address)
                    self.assertEqual(response.status_code, cond)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            reverse(
                const_value.URL_INDEX
            ): const_value.TEMPLATE_INDEX,
            reverse(
                const_value.URL_GROUP_LIST,
                args=[PostURLTests.group.slug]
            ): const_value.TEMPLATE_GROUP_LIST,
            reverse(
                const_value.URL_PROFILE,
                args=[PostURLTests.post.author]
            ): const_value.TEMPLATE_PROFILE,
            reverse(
                const_value.URL_POST_DETAIL,
                args=[PostURLTests.post.id]
            ): const_value.TEMPLATE_POST_DETAIL,
            reverse(
                const_value.URL_POST_EDIT,
                args=[PostURLTests.post.id]
            ): const_value.TEMPLATE_POST_EDIT,
            const_value.URL_UNEXISTING_PAGE:
                const_value.TEMPLATE_404_ERROR,
            reverse(
                const_value.URL_POST_CREATE
            ): const_value.TEMPLATE_POST_CREATE
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User
from posts.tests import const_value


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=const_value.USERNAME_AUTH)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=const_value.GROUP_TITLE_MAIN,
            slug=const_value.GROUP_SLUG_MAIN,
            description=const_value.GROUP_DESCRIPTION_MAIN,
        )
        cls.list_posts = []
        for create_post_number in range(const_value.NUMBERS_CREATE_POST):
            another_post = Post(
                author=cls.user,
                group=cls.group,
                text=f'{create_post_number} пост',
            )
            cls.list_posts.append(another_post)
        Post.objects.bulk_create(cls.list_posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        list_page = [
            reverse(
                const_value.URL_INDEX
            ),
            reverse(
                const_value.URL_GROUP_LIST,
                args=[PaginatorViewsTest.group.slug]
            ),
            reverse(
                const_value.URL_PROFILE,
                args=[PaginatorViewsTest.list_posts[0].author]
            ),
        ]
        posts_on_page = {
            const_value.FIRST_LIST_PAGINATOR: const_value.PRINT_TEN_POSTS,
            const_value.SECOND_LIST_PAGINATOR: const_value.PRINT_THREE_POSTS
        }
        for site in list_page:
            for page, posts in posts_on_page.items():
                with self.subTest(site=site):
                    response = self.client.get(site, {'page': page})
                    self.assertEqual(
                        len(response.context['page_obj']),
                        posts
                    )

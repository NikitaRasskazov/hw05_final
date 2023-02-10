import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms

from posts.models import Post, Group, User, Follow, Comment
from posts.tests import const_value

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
        cls.group_2 = Group.objects.create(
            title=const_value.GROUP_TITLE_TEST,
            slug=const_value.GROUP_SLUG_TEST,
            description=const_value.GROUP_DESCRIPTION_TEST,
        )
        cls.small_gif = const_value.SMALL_GIF
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type=const_value.NAME_IMAGE_GIF
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=const_value.POST_TEXT_MAIN,
            group=cls.group,
            image=cls.uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.another_author = User.objects.create_user(
            username=const_value.ANOTHER_AUTHOR
        )
        self.another_author_authorized = Client()
        self.another_author_authorized.force_login(self.another_author)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def check_context_template(self, values_context):
        values_context = {
            values_context.text: self.post.text,
            values_context.author: self.post.author,
            values_context.group: self.group,
            values_context.image: self.post.image
        }
        for context, values in values_context.items():
            self.assertEqual(context, values)

    def test_about_page_uses_correct_template(self):
        templates_page_names = {
            reverse(
                const_value.URL_INDEX
            ): const_value.TEMPLATE_INDEX,
            reverse(
                const_value.URL_GROUP_LIST,
                args=[PostPagesTests.post.group.slug]
            ): const_value.TEMPLATE_GROUP_LIST,
            reverse(
                const_value.URL_PROFILE,
                args=[PostPagesTests.post.author]
            ): const_value.TEMPLATE_PROFILE,
            reverse(
                const_value.URL_POST_DETAIL,
                args=[PostPagesTests.post.id]
            ): const_value.TEMPLATE_POST_DETAIL,
            reverse(
                const_value.URL_POST_EDIT,
                args=[PostPagesTests.post.id]
            ): const_value.TEMPLATE_POST_EDIT,
            reverse(
                const_value.URL_POST_CREATE
            ): const_value.TEMPLATE_POST_CREATE,
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template
                )

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(const_value.URL_INDEX))
        first_object = response.context[const_value.PAGE_OF_PAGINATOR][0]
        self.check_context_template(
            first_object
        )

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            const_value.URL_GROUP_LIST,
            args=[PostPagesTests.group.slug]
        ))
        first_object = response.context[const_value.PAGE_OF_PAGINATOR][0]
        self.check_context_template(first_object)
        self.assertNotEqual(
            response.context.get('group'),
            PostPagesTests.group_2
        )

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            const_value.URL_PROFILE,
            args=[const_value.USERNAME_AUTH]
        ))
        first_object = response.context[const_value.PAGE_OF_PAGINATOR][0]
        self.check_context_template(
            first_object
        )

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            const_value.URL_POST_DETAIL,
            args=[PostPagesTests.post.id]
        ))
        first_object = response.context['post']
        self.check_context_template(
            first_object
        )

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            const_value.URL_POST_CREATE
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected
                )

    def test_edit_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            const_value.URL_POST_EDIT,
            kwargs={'post_id': PostPagesTests.post.id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected
                )

    def test_cashe(self):
        test_post = Post.objects.create(
            text=const_value.POST_TEXT_TEST,
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(reverse(
            const_value.URL_INDEX
        ))
        create_post = response.context[const_value.PAGE_OF_PAGINATOR][0]
        self.assertEqual(test_post, create_post)
        test_post.delete()
        response_after_delete_post = self.authorized_client.get(reverse(
            const_value.URL_INDEX
        ))
        self.assertEqual(response.content, response_after_delete_post.content)
        cache.clear()
        response_after_update_cashe = self.authorized_client.get(reverse(
            const_value.URL_INDEX
        ))
        self.assertNotEqual(
            response.content,
            response_after_update_cashe.content
        )

    def test_following(self):
        self.another_author_authorized.get(reverse(
            const_value.URL_FOLLOWING,
            args=[self.user.username]
        ))
        self.assertEqual(
            Follow.objects.filter(
                author=self.user,
                user=self.another_author
            ).exists(), True
        )

    def test_unfollowing(self):
        self.another_author_authorized.get(reverse(
            const_value.URL_FOLLOWING,
            args=[self.user.username]
        ))
        count_followers = Follow.objects.count()
        self.another_author_authorized.get(reverse(
            const_value.URL_UNFOLLOW,
            args=[self.user.username]
        ))
        self.assertEqual(count_followers - 1, Follow.objects.count())
        self.assertEqual(
            Follow.objects.filter(
                author=self.user,
                user=self.another_author
            ).exists(), False
        )

    def test_do_not_show_post_for_unfollowers(self):
        response = self.another_author_authorized.get(reverse(
            const_value.URL_FOLLOW_INDEX
        ))
        any_object = response.context[const_value.PAGE_OF_PAGINATOR]
        self.assertEqual(len(any_object), 0)

    def test_following_yourself(self):
        self.authorized_client.get(reverse(
            const_value.URL_FOLLOWING,
            args=[self.user.username]
        ))
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.user
            ).exists()
        )

    def test_following_guest_client(self):
        follows_count = Follow.objects.count()
        self.guest_client.get(reverse(
            const_value.URL_FOLLOWING,
            args=[self.user.username]
        ))
        self.assertEqual(Follow.objects.count(), follows_count)

    def test_create_comments(self):
        comments_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': const_value.COMMENT_TEXT,
        }
        response = self.authorized_client.post(
            reverse(const_value.URL_CREATE_COMMENT, args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=const_value.COMMENT_TEXT,
            ).exists()
        )
        comment_additional = response.context['comments'][0]
        self.assertEqual(comment_additional.post, self.post)
        self.assertEqual(comment_additional.author, self.user)
        self.assertEqual(comment_additional.text, form_data['text'])

    def test_guest_client_notcreate_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'author': self.user,
            'text': const_value.COMMENT_TEXT,
        }
        self.guest_client.post(
            reverse(const_value.URL_CREATE_COMMENT, args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertFalse(
            Comment.objects.filter(
                text=const_value.COMMENT_TEXT
            ).exists()
        )

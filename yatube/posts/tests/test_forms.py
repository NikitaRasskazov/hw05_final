import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm
from posts.models import Post, Group, User
from posts.tests import const_value

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=const_value.USERNAME_AUTH)
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
        cls.post = Post.objects.create(
            author=cls.user,
            text=const_value.POST_TEXT_MAIN,
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostCreateFormTests.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def test_form_create_post(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': const_value.POST_TEXT_TEST,
            'group': PostCreateFormTests.group.id,
            'image': uploaded,
        }
        response = self.authorized_client_author.post(
            reverse(const_value.URL_POST_CREATE),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            const_value.URL_PROFILE,
            args=[PostCreateFormTests.post.author]
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            Post.objects.get(text=const_value.POST_TEXT_TEST).text,
            form_data['text']
        )
        self.assertEqual(
            Post.objects.get(text=const_value.POST_TEXT_TEST).group.id,
            form_data['group']
        )

    def test_form_edit_post(self):
        post_for_test = self.post
        form_data = {
            'text': const_value.EDIT_TEXT_POST,
            'group': PostCreateFormTests.group_2.id,
        }
        response = self.authorized_client_author.post(
            reverse(const_value.URL_POST_EDIT, args=[self.post.id]),
            data=form_data,
            follow=True
        )
        redact_post = Post.objects.get(text=const_value.EDIT_TEXT_POST)
        self.assertRedirects(response, reverse(
            const_value.URL_POST_DETAIL,
            args=[self.post.id]
        ))
        self.assertNotEqual(redact_post.text, post_for_test.text)

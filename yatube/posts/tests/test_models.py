from django.test import TestCase

from ..models import Group, Post, User, NUMBER_OF_CHARACTERS
from posts.tests import const_value


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=const_value.USERNAME_AUTH)
        cls.group = Group.objects.create(
            title=const_value.GROUP_TITLE_MAIN,
            slug=const_value.GROUP_SLUG_MAIN,
            description=const_value.GROUP_DESCRIPTION_MAIN,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=const_value.POST_TEXT_MAIN,
        )

    def test_models_have_correct_object_names(self):
        str_name_model_post_group = {
            PostModelTest.group.title: str(PostModelTest.group),
            PostModelTest.post.text[
                :NUMBER_OF_CHARACTERS
            ]: str(PostModelTest.post)
        }
        for expected, str_name_model in str_name_model_post_group.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, str_name_model)

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.files.base import ContentFile, BytesIO
from PIL import Image

from .models import PicturePost

def create_post(test, desc, source=''):
    picture = create_image(None, 'test.png')
    return PicturePost.objects.create(
        picture = SimpleUploadedFile('test.png', picture.getvalue()),
        name = test,
        description = desc,
        source = source
        )

def create_image(storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):
    """
    Generate a test image, returning the filename that it was saved as.

    If ``storage`` is ``None``, the BytesIO containing the image data
    will be passed instead.
    """
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    if not storage:
        return data
    image_file = ContentFile(data.read())
    return storage.save(filename, image_file)

class PicturePostIndexViewTests(TestCase):
    def test_no_posts(self):
        """
        Without posts display message.
        """
        response = self.client.get(reverse('photogallery:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts were found.")
        self.assertQuerysetEqual(response.context['pictures_list'], [])

    def test_posted(self):
        """
        Show posts when they exist.
        """
        create_post("Test 1", "Test 1 desc")
        response = self.client.get(reverse('photogallery:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['pictures_list'], ['<PicturePost: Test 1>'])

    def test_show_new_first(self):
        """
        Show posts when they exist.
        """
        create_post("Test 1", "Test 1 desc")
        create_post("Test 2", "Test 2 desc")
        response = self.client.get(reverse('photogallery:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['pictures_list'],
            ['<PicturePost: Test 2>', '<PicturePost: Test 1>']
        )

class PicturePostDetailViewTests(TestCase):
    def test_post_details(self):
        """
        Show details of post.
        """
        post = create_post("Test 3", "Test 3 desc")
        url = reverse('photogallery:detail', args=(post.id,))
        response = self.client.get(url)
        self.assertContains(response, post.name)
    
    def test_post_has_no_source(self):
        """
        Checks if there is option to click source if picture does not have one.
        """
        post = create_post("Test 3", "Test 3 desc")
        url = reverse('photogallery:detail', args=(post.id,))
        response = self.client.get(url)
        self.assertNotContains(response, "Source of Picture")

    def test_post_has_source(self):
        """
        Checks if there is option to click source if picture has one.
        """
        post = create_post("Test 3", "Test 3 desc", "Test Source")
        url = reverse('photogallery:detail', args=(post.id,))
        response = self.client.get(url)
        self.assertContains(response, "Source of Picture")

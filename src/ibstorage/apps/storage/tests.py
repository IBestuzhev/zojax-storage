"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import simplejson
from django.core.files.base import ContentFile
from django.core import mail

from storage.models import UserFile


class BasicTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'test@mail.com', 'test')
        upload = UserFile.objects.create(public=False, user=user)
        upload.file.save("testfile.txt", ContentFile("Test text"))
        self.uploaded_id = upload.id

    def tearDown(self):
        User.objects.get(username='test').uploads.all().delete()

    def test_basic(self):
        # Test that main page is acceptable
        resp = self.client.get('/')
        self.assertTemplateUsed(resp, 'index.html')

    def test_login(self):
        # Test that auth mechanism works
        resp = self.client.get('/list-files/')
        self.assertEqual(resp.status_code, 200)
        data = simplejson.loads(resp.content)
        self.assertTrue('login' in data, "Auth mechanism failure")
        self.client.login(username='test', password='test')

        resp = self.client.get('/list-files/')
        data = simplejson.loads(resp.content)
        self.assertTrue('filelist' in data)

    def test_upload(self):
        # Test file upload
        self.client.login(username='test', password='test')
        resp = self.client.get('/list-files/')
        data = simplejson.loads(resp.content)
        self.assertEqual(len(data['filelist']['files']), 1)

        resp = self.client.get('/upload/')
        data = simplejson.loads(resp.content)
        self.assertTrue('fileupload' in data)

        f = open('README.rst')
        resp = self.client.post('/upload/', {"public": True, "file": f})
        data = simplejson.loads(resp.content)
        self.assertTrue('redirect' in data)

        resp = self.client.get('/list-files/')
        data = simplejson.loads(resp.content)
        self.assertEqual(len(data['filelist']['files']), 2)

    def test_file_view(self):
        self.client.logout()

        # Test redirect from direct URL to ajax URL
        resp = self.client.get('/file/%d/'%self.uploaded_id)
        self.assertRedirects(resp, '/#!/file/%d/'%self.uploaded_id)

        # Test Not found message
        resp = self.client.get('/file/%d/'%self.uploaded_id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = simplejson.loads(resp.content)
        self.assertTrue('fileinfo' in data)
        self.assertTrue('errorMsg' in data['fileinfo'])

        # Test file metadata
        self.client.login(username='test', password='test')
        resp = self.client.get('/file/%d/'%self.uploaded_id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = simplejson.loads(resp.content)
        self.assertTrue('fileinfo' in data)
        self.assertTrue('info' in data['fileinfo'])

    def test_sharing(self):
        # Test send sharing mails
        self.client.login(username='test', password='test')
        resp = self.client.get('/share/%d/'%self.uploaded_id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = simplejson.loads(resp.content)
        self.assertTrue('sharebox' in data)

        resp = self.client.post('/share/%d/'%self.uploaded_id, {'emails': ''})
        data = simplejson.loads(resp.content)
        self.assertTrue('sharebox' in data)
        self.assertTrue('errorlist' in data['sharebox']['form'])

        resp = self.client.post('/share/%d/'%self.uploaded_id, {'emails': 'invalidmail'})
        data = simplejson.loads(resp.content)
        self.assertTrue('sharebox' in data)
        self.assertTrue('errorlist' in data['sharebox']['form'])

        resp = self.client.post('/share/%d/'%self.uploaded_id, {'emails': 'valid@mail.com'})
        data = simplejson.loads(resp.content)
        self.assertTrue('redirect' in data)
        self.assertGreater(len(mail.outbox), 0)
        self.assertEqual(mail.outbox[0].to, [u'valid@mail.com'])
from selenium import webdriver
import unittest
from app import create_app, db
from app.models import Role, User, Post
import threading
import re


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        try:
            # usage: http://chromedriver.chromium.org/getting-started
            SELENIUM_CHROMEDRIVER_PATH = 'D:\\chromedriver.exe'
            cls.client = webdriver.Chrome(SELENIUM_CHROMEDRIVER_PATH)
            #cls.client.implicitly_wait(5)
        except:
            pass
        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='jyj@chinabluedon.cn', username='root', password='123', role=admin_role,
                         confirmed=True)
            db.session.add(admin)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            db.drop_all()
            db.session.remove()

            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!', self.client.page_source))

        self.client.find_element_by_link_text('Sign In').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)

        self.client.find_element_by_name('email').send_keys('jyj@chinabluedon.cn')
        self.client.find_element_by_name('password').send_keys('123')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Hello,\s+root!', self.client.page_source))

        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>root</h1>' in self.client.page_source)

from setuptools import setup, find_packages

setup(
    name='myblog_flask',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'alembic>=0.9.9',
        'bleach>=2.1.3',
        'blinker>=1.4',
        'click>=6.7',
        'dominate>=2.3.1',
        'Flask>=1.0.2',
        'Flask-Bootstrap>=3.3.7.1',
        'Flask-HTTPAuth>=3.2.4',
        'Flask-Login>=0.4.1',
        'Flask-Mail>=0.9.1',
        'Flask-Migrate>=2.2.1',
        'Flask-Moment>=0.6.0',
        'Flask-PageDown>=0.2.2',
        'Flask-Script>=2.0.6',
        'Flask-SQLAlchemy>=2.3.2',
        'Flask-WTF>=0.14.2',
        'ForgeryPy>=0.1',
        'html5lib>=1.0.1',
        'itsdangerous>=0.24',
        'Jinja2>=2.10',
        'Mako>=1.0.7',
        'Markdown>=2.6.11',
        'MarkupSafe>=1.0',
        'python-dateutil>=2.7.3',
        'python-editor>=1.0.3',
        'six>=1.11.0',
        'SQLAlchemy>=1.2.8',
        'visitor>=0.1.3',
        'webencodings>=0.5.1',
        'Werkzeug>=0.14.1',
        'WTForms>=2.2.1'
    ]
)

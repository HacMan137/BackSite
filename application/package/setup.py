import setuptools

setuptools.setup(
    name="backsite",
    version="1.0.0",
    author="Adam Nichols",
    description="Package for BackSite web API",
    classifiers=[
        "Programming Language :: Python :: 3"
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        "psycopg2-binary==2.9.6",
        "sqlalchemy==2.0.12",
        "flask==2.3.2",
        "flask-cors==3.0.10",
        "gunicorn==20.1.0",
        "sqlalchemy-utils==0.41.1",
    ],
    package_dir={"": "src"},
    packages=[
        "backsite",
        "backsite.db",
        "backsite.db.management",
        "backsite.db.schema",
        "backsite.db.connection",
        "backsite.app",
        "backsite.utils",
    ]
)
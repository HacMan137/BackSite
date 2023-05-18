import setuptools

setuptools.setup(
    name="backsite_jobs",
    version="1.0.0",
    author="Adam Nichols",
    description="Package for BackSite Background Jobs",
    classifiers=[
        "Programming Language :: Python :: 3"
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        "psycopg2-binary==2.9.6",
        "sqlalchemy==2.0.12",
        "sqlalchemy-utils==0.41.1",
        "pika==1.3.2"
    ],
    package_dir={"": "src"},
    packages=[
        "backsite_jobs",
    ]
)
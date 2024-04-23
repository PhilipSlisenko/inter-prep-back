from setuptools import find_packages, setup

setup(
    name="",
    version="0.1.0",
    # description="A brief description of your package",
    # long_description="A longer description of your package",
    url="",
    install_requires=[
        "fastapi",
        "uvicorn",
        "typer[all]",
        "SQLAlchemy",
        "psycopg2-binary",
        "httpx",
        "openai",
        "stripe",
        "python-jose",
    ],
    classifiers=[],
)

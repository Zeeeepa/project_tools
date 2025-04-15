import os
from setuptools import find_packages
from setuptools import setup

folder = os.path.dirname(__file__)
version_path = os.path.join(folder, "src", "projects_tools", "version.py")

__version__ = None
with open(version_path) as f:
    exec(f.read(), globals())

req_path = os.path.join(folder, "requirements.txt")
install_requires = []
if os.path.exists(req_path):
    with open(req_path) as fp:
        install_requires = [line.strip() for line in fp]

readme_path = os.path.join(folder, "README.md")
readme_contents = ""
if os.path.exists(readme_path):
    with open(readme_path) as fp:
        readme_contents = fp.read().strip()

setup(
    name="projects_tools",
    version=__version__,
    description="Projects Tools: A tool for managing projects",
    author="allwefantasy",
    long_description=readme_contents,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'projects = projects_tools.cli.commands:main',
        ]        
    },
    package_dir={"": "src"},
    packages=find_packages("src"),    
    package_data={
        "projects_tools": [            
            "templates/*.jinja2"
        ],
    },
    install_requires=install_requires + [
        'jinja2>=3.0.0',
        'click>=8.0.0',
        'rich>=10.0.0',
        'requests>=2.28.0',
        'sqlalchemy>=2.0.0',
        'pytest>=7.0.0',
        'fastapi>=0.95.0',
        'uvicorn>=0.21.0',
        'httpx>=0.24.0',
        'aiofiles>=0.8.0',
    ],
    classifiers=[        
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)

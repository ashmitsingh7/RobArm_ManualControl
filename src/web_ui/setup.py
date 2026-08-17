from setuptools import setup
import os
from glob import glob

package_name = 'web_ui'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'static'), glob('static/*')),
    ],
    install_requires=['setuptools', 'aiohttp'],
    zip_safe=True,
    maintainer='Forge Dev',
    maintainer_email='user@example.com',
    description='Web-based control UI for robotic arm',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'web_server = web_ui.web_server:main',
        ],
    },
)

from setuptools import find_packages, setup

package_name = 'ros_bt'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='keerthi',
    maintainer_email='keerthi@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'esp_read_enc_merger = ros_bt.esp_read_enc_merger:main',
            'espA_read_enc= ros_bt.espA_read_enc:main',
            'espB_read_enc= ros_bt.espB_read_enc:main',
            'ros_write_motors_espA=ros_bt.ros_write_motors_espA:main',
            'ros_write_motors_espB=ros_bt.ros_write_motors_espB:main',
            # USB-only versions (alternate control path, no Bluetooth/rfcomm needed)
            'ros_write_motors_espA_usb=ros_bt.ros_write_motors_espA_usb:main',
            'ros_write_motors_espB_usb=ros_bt.ros_write_motors_espB_usb:main',
        ],
    },
)

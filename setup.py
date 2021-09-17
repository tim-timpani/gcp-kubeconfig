from setuptools import setup, find_packages

setup(
    name='gcp_kubeconfig',
    version='1.0.0',
    packages=find_packages(include=['gcp_kubeconfig', 'gcp_kubeconfig.*']),
    python_requires='>=3.5',
    url='',
    license='',
    author='Tim Martin',
    author_email='timothy.martin@netapp.com',
    description='Programmatically build gcp kubeconfig',
    install_requires=[
        'google-api-core==2.0.1',
        'google-cloud-container==2.7.1',
        'PyYAML==5.4.1'
    ],
    entry_points={
        'console_scripts': ['gcp-kubeconfig=gcp_kubeconfig.main:main']
    }
)

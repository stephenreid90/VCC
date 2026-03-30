from setuptools import setup, find_packages

setup(
    name='vcc-valuations',
    version='0.1.0',
    description='Production financial valuation engine for corporates, miners, banks',
    author='Ben Watson',
    author_email='ben@example.com',
    packages=find_packages(),
    install_requires=[
        'pydantic>=2.0',
        'pandas>=2.0',
        'numpy>=1.24',
        'openpyxl>=3.0',
        'scipy>=1.11.0',
        'matplotlib>=3.7',
        'plotly>=5.14',
        'fastapi>=0.100',
        'uvicorn>=0.23',
    ],
    extras_require={
        'dev': ['pytest>=7.4', 'pytest-cov>=4.1', 'jupyter>=1.0', 'jupyterlab>=4.0'],
    },
    python_requires='>=3.10',
)

"""
ZORIA Setup Configuration
Web-Based Interactive Dashboard for Impedance Analysis
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="zoria",
    version="1.0.0",
    author="Mario Ricardo Montero, Juan Carlos Alvarez, Francisco J. Racedo N.",
    author_email="mariomontero942@gmail.com",
    description="Web-Based Interactive Dashboard for Impedance Analysis and Circuit Characterization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mario1027/ZORIA",
    project_urls={
        "Bug Tracker": "https://github.com/mario1027/ZORIA/issues",
        "Documentation": "https://github.com/mario1027/ZORIA#readme",
        "Source Code": "https://github.com/mario1027/ZORIA",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: Dash",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pylint>=2.15.0",
            "black>=22.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "zoria=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.css", "*.js", "*.png", "*.jpg", "*.svg", "*.ini"],
    },
    keywords=[
        "impedance analysis",
        "lcr meter",
        "eval-admx2001",
        "analog devices",
        "electrochemical impedance spectroscopy",
        "circuit characterization",
        "bode plot",
        "nyquist plot",
        "rlc simulator",
        "data visualization",
        "dash",
        "plotly",
    ],
    zip_safe=False,
)

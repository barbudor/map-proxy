def get_version():
    with open("tdmgr.py", "r") as tdmgr:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  tdmgr.read(), re.M)
        return version_match.group(1)

setup(
    name="map-proxy",
    version=get_version(),
    description="Translate non OSM map tile server to OSM style",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/barbudor/map-proxy",
    author="barbudor (Jean-Michel Mercier)",
    author_email="barbudor@barbudor.net",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["map-proxy"],
    include_package_data=True,
    install_requires=[
        "requests"
    ],
    entry_points=None
)
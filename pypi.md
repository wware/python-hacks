# uploading to test.pypi

    rm -rf dist/*
    python setup.py sdist
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# retrieving

In the destination, set up a venv

    python -m virtualenv venv
    source venv/bin/activate
    curl https://bootstrap.pypa.io/get-pip.py | python     # Ubuntu pip sucks
    pip install -r requirements.txt      # get these from regular pypi
    pip install -i https://test.pypi.org/simple/ wware-hacks==0.0.x

then run tests

exclude any pytest stuff, it does not work well as part of a package

only put in the things that really belong in a package, split the rest off
into a side directory

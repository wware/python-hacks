#!/bin/bash -xe

# What follows is equivalent to "source venv/bin/activate"
# See https://gist.github.com/datagrok/2199506
# The deactivate happens automatically when the script ends
VIRTUAL_ENV=$(readlink -f venv)
PATH="$VIRTUAL_ENV/bin:$PATH"
export VIRTUAL_ENV PATH
unset PYTHON_HOME

if [ ! -d "${VIRTUAL_ENV}" ]
then
    virtualenv -p "$(which python3)" "${VIRTUAL_ENV}"
    pip install pytest==3.6 pytest-cov==2.5
fi

echo "NOW DO SOMETHING LIKE: py.test --cov=test_foo --doctest-module"

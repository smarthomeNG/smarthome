Testing SmartHomeNG
===================

As many Python projects SmartHomeNG also has quite a couple of test to check 
parts of the core and some plugins functionality. 

The tests are created as unittest Testcases. The tests for the core can be found in ``tests/``

The requirements to run tests are found in ``requirements/test.txt`` and can be installed
using ``pip3 install -r requirements/test.txt --user``

To **run a full test** for SmartHomeNG start ``pytest -v``
in the home directory of SmartHomeNG (normally ``/usr/local/smarthome``)

With the above statement pytest will search all subdirectories for test cases.

If **only a test for a specific plugin** should be run, then the command ``pytest -v ../plugin/<name of plugin>``
needs to be called from within the tests directory (normally ``/usr/local/smarthome/tests``)

Pytest will also use the settings from tox.ini but additionally to the test directories the ``tests`` 
directory will be included in the search path. If this would not be the case, then all common definitions
could not be used by the test.

Create tests for a plugin
=========================

1. create a subdirectory named ``tests`` within your plugin.
2. Create a test case in a file starting with ``test_`` like ``test_calculations.py``. 
   Otherwise pytest can not find it. There is a sample included within the ``dev\sample_plugin\tests``
   which can be used for scaffolding.
3. Add tests to your testclass that start with ``test`` as method names
4. Run the tests from 
   and have them successfullefor your plugin before you push to the develop branch

Test discovery with pytest
==========================

pytest implements the following standard test discovery:

* If no arguments are specified then collection starts from testpaths (if configured) or the current directory. 
  Alternatively, command line arguments can be used in any combination of directories, file names or node ids.
* Recurse into directories, unless they match norecursedirs.
* In those directories, search for ``test_*.py`` or ``*_test.py`` files, imported by their test package name.
* From those files, collect test items:
  * test prefixed test functions or methods outside of class
  * test prefixed test functions or methods inside Test prefixed test classes (without an __init__ method)

Within Python modules, pytest discovers tests using the standard ``unittest.TestCase`` subclassing technique.

Pytest will look inside ``tox.ini`` to find out the files to use for test cases.

.. code:: ini

    [tox]
    ;envlist = py34, lint
    ; tox roughly follows the following phases:
    ; 1. configuration: 
    ;    load tox.ini and merge it with options from the command line and the operating system environment variables.
    ; 2. packaging (optional):
    ;    create a source distribution of the current project by invoking ``python setup.py sdist``
    ;    Note that for this operation the same Python environment will be used as the one tox is
    ;    installed into (therefore you need to make sure that it contains your build dependencies).
    ;    Skip this step for application projects that don’t have a setup.py.
    ; 3. environment - for each tox environment (e.g. py27, py36) do:
    ;    a. environment creation:
    ;       create a fresh environment, by default virtualenv is used. 
    ;       tox will automatically try to discover a valid Python interpreter version by
    ;       using the environment name (e.g. py27 means Python 2.7 and the basepython configuration value)
    ;       and the current operating system PATH value.
    ;       This is created at first run only to be re-used at subsequent runs.
    ;       If certain aspects of the project change, a re-creation of the environment is
    ;       automatically triggered. To force the recreation tox can be invoked with -r/--recreate.
    ;    b. install (optional):
    ;       install the environment dependencies specified inside the deps configuration section,
    ;       and then the earlier packaged source distribution.
    ;       By default pip is used to install packages, however one can customise this
    ;       via install_command. Note pip will not update project dependencies 
    ;       (specified either in the install_requires or the extras section of the setup.py) 
    ;       if any version already exists in the virtual environment; therefore we recommend
    ;       to recreate your environments whenever your project dependencies change.
    ;    c. commands: 
    ;       run the specified commands in the specified order. Whenever the exit code
    ;       of any of them is not zero stop, and mark the environment failed.
    ;       Note, starting a command with a single dash character means ignore exit code.
    ;  6. report print out a report of outcomes for each tox environment:


    ; To run tests on Travis CI add the environments to the .travis.yml too!
    envlist = py35, py36, py37
    skip_missing_interpreters = True

    ; do not execute a ``python setup.py sdist``
    skipsdist=True

    [pytest]
    testpaths = tests plugins
    python_files = test_*.py
    python_functions = test_
    python_classes = Test

    [testenv]
    ; 3a
    setenv =
        LANG=de_DE.utf8
        TZ=UTC
        PYTHONPATH ={toxinidir}{:}{toxinidir}/tests{:}{toxinidir}/lib{:}{toxinidir}/bin
    ; update pip/wheel/setuptools etc.
    download=true
    ; prevent warnings 
    whitelist_externals = 
        head

    ; 3b
    deps = 
        -r{toxinidir}/requirements/test.txt
    ; 3c
    ; python3 tools/build_requirements.py  -debug_tox for debugging build_requirements.py and lib/shpypi.py
    commands =
        python3 tools/build_requirements.py 
        head {toxinidir}/requirements/base.txt -n 12
        head {toxinidir}/requirements/all.txt -n 12
        pip install -r {toxinidir}/requirements/base.txt
        pip install -r {toxinidir}/requirements/all.txt
        py.test -v --ignore=./plugins/database/tests --timeout=30 --cov --cov-report= {posargs}

    #[testenv:py35]
    #basepython = python3.5

    #[testenv:py36]
    #basepython = python3.6

    #[testenv:py37]
    #basepython = python3.7

    #[testenv:py38]
    #basepython = python3.8
    # there is no ruamel.yaml version 0.15.74 which is compatible with Python 3.8 as of April 13th, 2020

    [testenv:lint]
    basepython = python3
    ignore_errors = True
    commands =
        flake8
        pylint bin/smarthome.py
        pydocstyle tests



Continuous integration test with Travis CI
==========================================

At `https://travis-ci.org/github/smarthomeNG/smarthome`_ the last test results can be seen.
The actions that Travis will perform each time a new commit is pushed to the SmartHomeNG repository are
declared in ``.travis.yml`` and ``.travis.sh``.

.. code:: yaml

    language: python

    jobs:
        include:
          - python: 3.5
          - python: 3.6
          - python: 3.7
            dist: xenial

    # need to allow ruamel.yaml higher than 0.15.74 to support Python 3.8
    #      - python: 3.8
    #        dist: xenial

    env:
        - REPOSITORY_ORIGIN=smarthome

    before_install:
        - sudo apt-get install libudev-dev
        - sudo apt-get install librrd-dev libpython3-dev
    install:
        - pip install tox-travis virtualenv
        - pip install sphinx sphinx_rtd_theme recommonmark

    script:
        - sh .travis.sh


.. code:: bash

    #######################################################################
    # Travis-CI script
    #
    # This script will checkout all required reqository to run the
    # suite.
    #
    # The following configuration settings are available:
    # * Environment settings:
    #   - REPOSITORY_ORIGIN: defines the current repos origin (e.g.
    #     "smarthome" or "plugins")
    # * Script settings:
    #   - REPOSITORIES: List of repositories to checkout from smarthomeNG
    #     organization (e.g. "https://github.com/smarthomeNG/<repo-name>")
    #   - LINKS: Contains a list of links to create before running the
    #     suite (e.g. "<target-repo>/<target-dir>/<source-repo>")
    # * Script variables:
    #   - REPOSITORY: The name of the current repository
    #   - REPOSITORY_ORIGIN: The origin repository from environment setting
    #   - REPOSITORY_BRANCH: The branch to use for checkouts

    echo -e "travis_fold:start:Environment\nEnvironment dump"
    set
    export
    echo "travis_fold:end:Environment"

    #######################################################################
    # Declare some common variables

    REPOSITORIES="smarthome plugins"
    LINKS="smarthome/plugins/plugins"

    # Get the current repository which is processed
    REPOSITORY="$(basename $TRAVIS_REPO_SLUG)"
    REPO_OWNER="$(dirname  $TRAVIS_REPO_SLUG)"
    REPOSITORY_ORIGIN="$REPOSITORY_ORIGIN"

    # Find out on which branch to work
    #if [ "$TRAVIS_BRANCH" = "master" ] ; then
    #  REPOSITORY_BRANCH="master"
    #else
    #  REPOSITORY_BRANCH="develop"
    #fi

    REPOSITORY_BRANCH=$TRAVIS_BRANCH
    echo -e "Current branch for $REPOSITORY is $REPOSITORY_BRANCH"

    #######################################################################
    # 1. Checkout all repositories

    echo -e "travis_fold:start:Checkout\nChecking out additional repositories with $REPOSITORY_BRANCH branch"

    # Change to root directory since script is started in checkout
    cd $TRAVIS_BUILD_DIR/..

    # Check out other repositories with develop version
    for REPO in $REPOSITORIES ; do
      if [ "$REPO" != "$REPOSITORY_ORIGIN" ] ; then
        echo "Checking out $REPO ..."
        git clone https://github.com/$REPO_OWNER/$REPO.git $REPO
        cd $REPO
        git checkout $REPOSITORY_BRANCH
        cd ..
      fi
    done

    echo "travis_fold:end:Checkout"


    #######################################################################
    # 2. Create symlinks in repositories

    echo -e "travis_fold:start:Links\nCreating symlinks"

    # Create symlinks in core repository
    for LINK in $LINKS ; do
      TARGET=$(dirname "$LINK")
      TARGET_REPO=$(dirname "$TARGET")
      TARGET_DIR=$(basename "$TARGET")
      SOURCE_REPO=$(basename "$LINK")

      echo "Create link from $SOURCE_REPO to $TARGET_REPO/$TARGET_DIR ..."
      cd $TARGET_REPO
      rm -rf $TARGET_DIR
      ln -s ../$SOURCE_REPO $TARGET_DIR
      cd ..
    done

    echo "travis_fold:end:Links"


    #######################################################################
    # 3. Run

    echo -e "travis_fold:start:Suite\nRunning suite"

    cd smarthome
    #echo "would run tox now"
    tox || exit 1
    cd ..

    echo "travis_fold:end:Suite"


    #######################################################################
    # 4. Docs

    echo -e "travis_fold:start:Docs\nBuilding documentation"

    cd smarthome/doc
    #yes | bash build_doc.sh
    echo "would build docs here"
    cd ../..

    echo "travis_fold:end:Docs"

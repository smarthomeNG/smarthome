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
REPOSITORY_ORIGIN="$REPOSITORY_ORIGIN"

# Find out on which branch to work
if [ "$TRAVIS_BRANCH" = "master" ] ; then
  REPOSITORY_BRANCH="master"
else
  REPOSITORY_BRANCH="develop"
fi


#######################################################################
# 1. Checkout all repositories

echo -e "travis_fold:start:Checkout\nChecking out repositories with $REPOSITORY_BRANCH branch"

# Change to root directory since script is started in checkout
cd $TRAVIS_BUILD_DIR/..

# Check out other repositories with develop version
for REPO in $REPOSITORIES ; do
  if [ "$REPO" != "$REPOSITORY_ORIGIN" ] ; then
    echo "Checking out $REPO ..."
    git clone https://github.com/smarthomeNG/$REPO.git $REPO
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
tox || exit 1
cd ..

echo "travis_fold:end:Suite"


#######################################################################
# 4. Docs

#echo -e "travis_fold:start:Docs\nBuilding documentation"

#cd smarthome/doc
#yes | bash build_doc.sh
#cd ../..

#echo "travis_fold:end:Docs"

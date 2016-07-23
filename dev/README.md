
# Plugin developement

## GIT

For an git introduction to git see: [http://gitimmersion.com/](http://gitimmersion.com/)

It you want to publish your plugin, get an [github account](https://github.com/users) as soon as possible.

### Usefull commands
   * __list changes__ since the release with the tag VERSIONTAG: `git log --pretty=format:"%s" <VERSIONTAG>..HEAD`
   * __undo commit__ with the id XXXIDXXX: `git reset --hard XXXIDXXX && git push origin develop --force`
   * __copy commit__ to current branch: `git cherry-pick <commit>`

   Follow the [commit Atom Feed](https://github.com/smarthomeNG/smarthome/commits/develop.atom)

### Global settings
   * only push the current branch (not all): `git config --global push.default current`
   * adapt your user settings:
      * `git config --global user.name "Your Name"`
      * `git config --global user.email you@example.com`

### Branches
The repositry consist of three main branches:

  * __master__: it contains the stable/release code
  * __develop__: is the branch where new features and plugins are merged into
  * __gh-pages__: this branch contains the SmartHomeNG.py website 

The branch setup is based on [this model](http://nvie.com/posts/a-successful-git-branching-model/).

### Getting the Source
  * you could fork the repository on github or
  * get the repository: `git clone https://github.com/smarthomeNG/smarthome.git
  * create your own (local) branch (from develop) `git checkout -b myplugin develop`

## Python Version
You should only use Python =< 3.2 methods. If not make it clear in the documentation what kind of Python version you need.

## Coding style
Your code should conform to [pep 8](http://www.python.org/dev/peps/pep-0008/). (I'm ignoring "E501 line too long".)

## Start Coding
   * __copy__ the skeleton directory: `cp -r plugins/skeleton plugins/myplugin`
   * __edit__ the main file: `vi plugins/myplugin/__init__.py`

### Tools
Have a look at the following tools to test your code:

#### pep8
   * Install pep8: `apt-get install pep8` 
   * Test your code: `pep8 -qq --statistics yourcode.py`

#### autopep8
   * `pip-3.2 install autopep8`
   * `autopep8 yourcode.py -i`

#### flake8
   * `pip-3.2 install flake8`
   * `flake8 yourcode.py`

I'm using it as a vim plugin. It checks the code every time I save the file. Most usefull!

### Test and Document
Please test and document your code!
In your plugin directory should be a __README.md__ (from the skeleton directory). Please fill it with the neccesary information. `vi plugins/myplugin/README.md`

### Basic Rules
   * __only push to the develop branch__
   * changes to bin/smarthome.py and lib/\* must be checked with me.
   * changes to plugins from other developers must be checked with the developer.

### Fork
   * Goto [SmartHome Repo](https://github.com/smarthomeNG/smarthome) logged in with your username/password.
   * Click on 'fork' in the right upper corner.
   * Change to your Terminal and enter `git clone https://USER:PASSWORD@github.com/USER/smarthome`
   * Checkout the develop branch `git checkout develop`
   * Change/create a file.
   * Add the file `git add FILE`
   * Commit the changes with a usefull comment: 'git commit'
   * Push your changes to your repository: `git pull && git push`
   * Create a pull request on github: base: smarthomeNG/develop  compare: USER/develop


### Merge
If you think your code is ready for prime time send me a __pull request via github__ 

Acitve commiters could merge the myplugin branch into develop with:

   * __change__ the active branch to develop: `git checkout develop`
   * __merge__ your plugin into it: `git merge --no-ff myplugin`
   * (delete your branch: `git branch -d myplugin`)
   * __push__ to github: `git push origin develop`

#### .git/config
If you have problems pushing, you could check the repo git config. Mine looks like this:
<pre>
[remote "origin"]
    url = https://github.com/smarthomeNG/smarthome
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
    remote = origin
    merge = refs/heads/master
[branch "develop"]
    remote = origin
    merge = refs/heads/develop
</pre>

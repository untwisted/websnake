##############################################################################
# push, websnake, github.
cd ~/projects/websnake-code
git status
git add *
git commit -a
git push 
##############################################################################
# create the develop branch, websnake.
git branch -a
git checkout -b development
git push --set-upstream origin development
##############################################################################
# merge master into development, websnake.
cd ~/projects/websnake-code
git checkout development
git merge master
git push
##############################################################################
# merge development into master, websnake.
cd ~/projects/websnake-code
git checkout master
git merge development
git push
git checkout development
##############################################################################
# check diffs, websnake.
cd ~/projects/websnake-code
git diff
##############################################################################
# delete the development branch, websnake.
git branch -d development
git push origin :development
git fetch -p 
##############################################################################
# undo, changes, websnake, github.
cd ~/projects/websnake-code
git checkout *
##############################################################################
# install, websnake.
sudo bash -i
cd /home/tau/projects/websnake-code
python2 setup.py install
rm -fr build
exit
##############################################################################
# build, websnake, package, disutils.
cd /home/tau/projects/websnake-code
python2.6 setup.py sdist 
rm -fr dist
rm MANIFEST
##############################################################################
# share, put, place, host, package, python, pip, application, websnake.

cd ~/projects/websnake-code
python2 setup.py sdist register upload
rm -fr dist
##############################################################################





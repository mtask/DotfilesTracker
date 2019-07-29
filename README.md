# DotfilesTracker 

Script that automates "dotfiles" tracking using git.


# Basic Configuration

## Initial setup

This is just basic configuration for tracking dotfiles with git. Main idea is taken from Arch Linux wiki and from this blog post: https://medium.com/@augusteo/simplest-way-to-sync-dotfiles-and-config-using-git-14051af8703a.


```
$ git init --bare ~/.dotfiles
$ alias config='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
$ config config status.showUntrackedFiles no
```

Because my desktop configs are not compatible between each other I can't just track one version of dotfiles.
To manage this I create own branches for each machine. This requires that master branch is kept empty.

### Setup for initial machine

```
$ config checkout -b <desktop name>
$ config add ~/.bashrc 
$ config commit -m "Add bashrc" 
$ config remote add origin git@gitofchoice.com:yourname/dotfiles.git 
$ config push -u origin <desktop name>
```


### Setup for new machine

```
$ alias config='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME
$ config config status.showUntrackedFiles no
$ git clone --bare git@gitofchoice.com:yourname/dotfiles.git $HOME/.dotfiles
$ config checkout -b <desktop name>
$ config add ~/.bashrc
$ config commit -m "Add bashrc"
$ config push -u origin <desktop name>
```


## Tracking dotfiles automatically

### Concept

Even though basic setup works nicely I don't usually remember to commit changes when I edit something in tracked dotfiles.
This is the problem that this python tool is trying to solve. There might be better existing solutions for this but at least it does what I need.

 - Basic idea: 

   - Script takes list of dotfiles as an argument.
   - These files are monitored for new write events using inotify library.
   - When write event occurs file changes are pushed to git automatically. (This of course expects that ssh keys are setup for the git repo)

#### Setup

 - Script is made for Python3
 - Dependencies
   - `pip3 install pyinotify`
   - Other libraries: `sys, os, argparse, subprocess`



# Usage

`python src/dotfile_tracker.py -f "/home/myusername/.bashrc,/home/myusername/.config/i3/config" -u myusername -b machine_branch`

Arguments explained

 - `-f/--files <str/file>`

List of files to track in following form: "/path/.file1,/path/.file/,/path/.etc".

If you have lots of files to track you can also create file were one line always includes path to one file. 
Then just pass that file as an argument for `-f` option. E.g: `python dotfile_tracker -f /home/u/.trackthese`.

```
$ cat /home/m/.trackthese
/home/m/.bashrc
/home/m/.vimrc
/home/m/.emacs.d/init.el
/home/m/.config/i3/config
```

- `-u/--username`

Your *nix username which is used to create working directory path and repository folder path (if not overridden).

- `-b/--branch`

Git branch for pushing.

- `-p/--path` (optional)

Script assumes that dotfiles repo is in path `~/.dotfiles`.
You can override this with `-p <absolute path>`. Working directory is hard coded to `/home/<given username>`.


### Running script in the background
I run the script in background by launching it in i3 config:

`exec --no-startup-id python /home/m/git/DotfileTracker/src/dotfile_tracker.py -f /home/m/.trackthese -u m -b air1 >> /tmp/dotfiles.log &`

### Example output

```
$ python src/dotfile_tracker.py -f "/home/m/.bashrc,/home/m/.config/i3/config" -u m -b air1
[air1 b9a3b4f] dotfile_tracker update
 1 file changed, 3 insertions(+), 1 deletion(-)
Enumerating objects: 9, done.
Counting objects: 100% (9/9), done.
Delta compression using up to 4 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (5/5), 434 bytes | 434.00 KiB/s, done.
Total 5 (delta 2), reused 0 (delta 0)
remote: 
remote: To create a merge request for air1, visit:
remote:   ...
remote: 
To ...
   d83ed80..b9a3b4f  air1 -> air1
[!] Pushed changes in /home/m/.bashrc
```


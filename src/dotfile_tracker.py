import pyinotify
import argparse
import sys
import os
import subprocess

class Git(object):

    def __init__(self, user, branch):
        self.user = user
        self.branch = branch
        self.git_base = ["git", "--git-dir=/home/"+self.user+"/.dotfiles/", "--work-tree=/home/"+self.user]
 
    def post_change(self, add_file, commit_msg=""):
        self.commit = self.git_base + ["commit", "-m", commit_msg]
        self.add = self.git_base + ["add", add_file]
        self.push =  self.git_base + ["push", "origin", self.branch]
        try:
            subprocess.call(self.add)
            subprocess.call(self.commit)
            subprocess.call(self.push)
            print("[!] Pushed changes in "+add_file)
        except Exception as e:
            print("[!] Failed to push changes for " +add_file)
            raise e


class MyEventHandler(pyinotify.ProcessEvent):
    """
    This is a handler for new write events in monitored files
    """
    
    def __init__(self, git_obj):
        self.git = git_obj

    def process_IN_CLOSE_WRITE(self, event):
        """
        Post changes to git when a dotfile is updated
        """
        self.git.post_change(event.pathname, commit_msg="dotfile_tracker update")

def main(files, user, branch):
    # Git object
    git = Git(user, branch)
    # watch manager
    wm = pyinotify.WatchManager()
    for f in files:
        wm.add_watch(f, pyinotify.ALL_EVENTS, rec=True)

    # event handler
    eh = MyEventHandler(git)

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()

def parse_args():
    descr = """Monitor dotfiles and autocommit to git"""
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument("-f", "--files", type=str, help="Files to monitor", required=True)
    parser.add_argument("-u", "--username", type=str, help="System user which is used to create path for /home/<user>/.dotfiles", required=True)
    parser.add_argument("-b", "--branch", type=str, help="Git branch for push", required=True)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    if not args.files or not args.username or not args.branch:
        print(args.help)
        sys.exit()
    main(args.files.split(','), args.username, args.branch)

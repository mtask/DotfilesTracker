#!/usr/bin/env python3

import pyinotify
import argparse
import sys
import os
import subprocess

class Git(object):

    def __init__(self, user, branch, local_git_folder=""):
        self.user = user
        self.branch = branch
        self.local_git_folder = local_git_folder

        if self.local_git_folder == "":
            self.local_git_folder = "/home/"+self.user+"/.dotfiles/"

        print("[!] Local git repository folder: "+self.local_git_folder)
        self.git_base = ["git", "--git-dir="+self.local_git_folder, "--work-tree=/home/"+self.user]

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


class DotfileEventHandler(pyinotify.ProcessEvent):
    """
    This is a handler for new write events in monitored files
    """

    def __init__(self, git_obj):
        self.git = git_obj

    def process_IN_CLOSE_WRITE(self, event):
        """
        Post changes to git when a dotfile is updated
        """
        self.git.post_change(event.pathname, commit_msg="dotfile_tracker update: "+event.pathname)

def main(files, user, branch, local_git_folder=""):
    # Git object
    git = Git(user, branch, local_git_folder)
    # watch manager
    wm = pyinotify.WatchManager()

    print("[!] Monitoring following files:")
    for f in files:
        wm.add_watch(f, pyinotify.ALL_EVENTS, rec=True)
        print("-"+ f)

    # event handler
    eh = DotfileEventHandler(git)

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()

def already_running(pid_file_path="/tmp/.dotfile_tracker.pid"):
    my_pid = os.getpid()

    with open(pid_file_path, 'a+') as f:
        f.seek(0)
        try:
            pid = int(f.readline())
            os.kill(pid, 0)
            running = True
        except (ValueError, ProcessLookupError) as e:
            print(e)
            f.seek(0)
            f.truncate()
            f.write(str(my_pid))
            running = False
    return running


def parse_args():
    descr = """Monitor dotfiles and autocommit to git"""
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument("-f", "--files", type=str, help="Files to monitor. Accepts list of filenames seperated with comma or path to file were one targeted file per line", required=True)
    parser.add_argument("-u", "--username", type=str, help="System user which is used to create path for /home/<user>/", required=True)
    parser.add_argument("-b", "--branch", type=str, help="Git branch for push", required=True)
    parser.add_argument("-p", "--path", type=str, help="Override local path of git repo (use absolute path). Default is /home/<user>/.dotfiles", required=False)
    return parser.parse_args()

if __name__ == '__main__':
    # Parse args
    args = parse_args()
    if not args.files or not args.username or not args.branch:
        print(args.help)
        sys.exit()

    # Check if instance of script is already running
    if already_running():
        print("[!] Instance of script is already running.")
        sys.exit(0)


    # Check if path to repository folder was given
    if args.path:
        git_local_folder = args.path
    else:
        git_local_folder = ""

    # Check if files to monitor were gave as file or string
    if os.path.isfile(args.files):
        with open(args.files) as f:
            files_to_monitor = f.read().splitlines()
    else:
        files_to_monitor = args.files.split(',')
    main(files_to_monitor, args.username, args.branch, git_local_folder)

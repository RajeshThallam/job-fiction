import threading
import subprocess

class RunThread(threading.Thread):
    def __init__(self, params):
        self.params = params
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(self.params, shell=False, stdout=subprocess.PIPE)
        self.stdout, self.stderr = p.communicate()
import threading
from datetime import datetime
import time

import psutil

from config.config import Config


class Optimizer(threading.Thread):
    def __init__(self, i: int):
        super().__init__()
        self.i = i

    def run(self):
        done = False
        time.sleep(60)
        while True:
            if (datetime.now().minute % Config.instance.services.optimizer.frequency) == 0:
                if not done:
                    done = True
                    for proc in psutil.process_iter():
                        if 'chrome' in proc.name():
                            print(proc.cmdline())
                            try:
                                proc.kill()
                            except:
                                pass
            else:
                done = False
            time.sleep(5)
            print('{} {} {}'.format(datetime.now().minute,(datetime.now().minute % Config.instance.services.optimizer.frequency),done))
            # Initializer.deletetmp()
            # down chrome driver

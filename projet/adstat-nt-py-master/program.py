import sys
import time

from Services.optimizer import Optimizer
from Services.profilebuilder import ProfileBuilder
from Services.tracker import Tracker
from config.config import Config
from config.init import Initializer

if __name__ == '__main__':
    Config.load()
    Initializer.deletetmp()
    for i in range(Config.instance.services.builder.threads):
        service = ProfileBuilder(i)
        service.start()
        time.sleep(2.5)
    for i in range(Config.instance.services.tracker.threads):
        service = Tracker(i)
        service.start()
        time.sleep(2.5)
    for i in range(Config.instance.services.optimizer.threads):
        service = Optimizer(i)
        service.start()
        time.sleep(2.5)

    sys.exit(0)

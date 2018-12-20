import argparse
import logging
import multiprocessing
import time

import walkoff.config
from walkoff.worker.worker import Worker

logger = logging.getLogger(__name__)
should_exit = multiprocessing.Event()
should_exit.clear()


def parse_args():
    parser = argparse.ArgumentParser(description='Script to start WALKOFF Workflow workers')
    parser.add_argument('-n', '--num', help='Number of workers to spawn')
    parser.add_argument('-v', '--version', help='Get the version of WALKOFF running', action='store_true')
    parser.add_argument('-c', '--config', help='Configuration file to use')
    args = parser.parse_args()
    if args.version:
        print(walkoff.__version__)
        exit(0)

    return args


def spawn_worker_processes():
    """Initialize the multiprocessing pool, allowing for parallel execution of workflows.
    """
    pids = []
    try:
        for i in range(walkoff.config.Config.NUMBER_PROCESSES):
            pid = multiprocessing.Process(target=Worker, args=(i, walkoff.config.Config.CONFIG_PATH, should_exit))
            pid.start()
            pids.append(pid)
        return pids
    except KeyboardInterrupt:
        shutdown_procs(pids)


def shutdown_procs(procs):
    should_exit.set()
    for proc in procs:
        proc.join(timeout=3)  # allow the worker some time to exit cleanly before coming after it with fire
        if proc.is_alive():
            logger.info('Sending SIGKILL to process {}.'.format(proc.pid))
            proc.kill()
            proc.join()
            logger.info('Process {} killed.'.format(proc.pid))


if __name__ == '__main__':
    import sys
    args = parse_args()

    if args.config:
        walkoff.config.initialize(config_path=args.config)
    else:
        walkoff.config.initialize()

    processes = spawn_worker_processes()

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        shutdown_procs(processes)
    finally:
        sys.exit(0)

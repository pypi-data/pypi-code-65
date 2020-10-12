import fcntl

wlock = False
rlock = False

def write_lock():
    wlock = open(LOCKFILE, "w")
    fcntl.lockf(wlock, fcntl.LOCK_EX)


def write_unlock():
    fcntl.lockf(wlock, fcntl.LOCK_UN)


def read_lock():
    rlock = open(LOCKFILE, "r")
    fcntl.lockf(rlock, fcntl.LOCK_EX)


def read_unlock():
    fcntl.lockf(rlock, fcntl.LOCK_UN)

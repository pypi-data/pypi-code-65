import subprocess
import posix_ipc
import time
import os

# This variation on


# FIXME - the existing demo doesn't call sem.close(), so it's probably leaving a
# dingleberry behind. You might have to fix a bunch of demos and follow up with
# a blog post.

with posix_ipc.Semaphore(None, posix_ipc.O_CREX, initial_value=1) as sem:
    print("Parent: created semaphore {}.".format(sem.name))

    # Spawn a child that will wait on this semaphore.
    path, _ = os.path.split(__file__)
    print("Parent: spawning child process...")
    subprocess.Popen(["python", os.path.join(path, 'child.py'), sem.name])

    for i in range(3, 0, -1):
        print("Parent: child process will acquire the semaphore in {} seconds...".format(i))
        time.sleep(1)

    sem.release()

    # Sleep for a second to give the child a chance to acquire the semaphore.
    # This technique is a little sloppy because technically the child could still
    # starve, but it's certainly sufficient for this demo.
    time.sleep(1)

    # Wait for the child to release the semaphore.
    print("Parent: waiting for the child to release the semaphore.")
    sem.acquire()

print("Parent: destroying the semaphore.")
sem.release()
sem.close()
sem.unlink()

msg = """
By the time you're done reading this, the parent will have exited and so the
operating system will have destroyed the semaphore. You can prove that  the
semaphore is gone by running this command and observing that it raises
posix_ipc.ExistentialError --

   python -c "import posix_ipc; posix_ipc.Semaphore('{}')"

""".format(sem.name)

print(msg)

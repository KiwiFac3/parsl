''' Testing bash apps
'''
import parsl
from parsl import *

import os
import time
import shutil
import argparse

#parsl.set_stream_logger()

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)


@App('bash', dfk)
def increment(inputs=[], outputs=[], stdout=None, stderr=None):
    # Place double braces to avoid python complaining about missing keys for {item = $1}
    cmd_line = '''
    x=$(cat {inputs[0]})
    echo $(($x+1)) > {outputs[0]}
    '''

@App('bash', dfk)
def slow_increment(dur, inputs=[], outputs=[], stdout=None, stderr=None):
    cmd_line = '''
    x=$(cat {inputs[0]})
    echo $(($x+1)) > {outputs[0]}
    sleep {0}
    '''


def test_increment(depth=5):
    ''' Test simple pipeline A->B...->N
    '''
    # Create the first file
    open("test0.txt", 'w').write('0\n')

    # Create the first entry in the dictionary holding the futures
    prev = "test0.txt"
    futs = {}
    for i in range(1,depth):
        print("Launching {0} with {1}".format(i, prev))
        fu, [prev] = increment(inputs=[prev], # Depend on the future from previous call
                               outputs=["test{0}.txt".format(i)], # Name the file to be created here
                               stdout="incr{0}.out".format(i),
                               stderr="incr{0}.err".format(i))
        futs[i] = prev
        print(prev.filepath)

    for key in futs:
        if key > 0 :
            fu = futs[key]
            data = open(fu.result(), 'r').read().strip()
            assert data == str(key), "[TEST] incr failed for key:{0} got:{1}".format(key, data)


def test_increment_slow(depth=5, dur=0.5):
    ''' Test simple pipeline A->B...->N
    '''
    # Create the first file
    open("test0.txt", 'w').write('0\n')

    # Create the first entry in the dictionary holding the futures
    prev = "test0.txt"
    futs = {}
    print("**************TYpe : ", type(dur), dur)
    for i in range(1,depth):
        print("Launching {0} with {1}".format(i, prev))
        fu, [prev] = slow_increment(dur,
                                    inputs=[prev], # Depend on the future from previous call
                                    outputs=["test{0}.txt".format(i)], # Name the file to be created here
                                    stdout="incr{0}.out".format(i),
                                    stderr="incr{0}.err".format(i))
        futs[i] = prev
        print(prev.filepath)

    for key in futs:
        if key > 0 :
            fu = futs[key]
            data = open(fu.result(), 'r').read().strip()
            assert data == str(key), "[TEST] incr failed for key:{0} got:{1}".format(key, data)


if __name__ == '__main__' :

    parser   = argparse.ArgumentParser()
    parser.add_argument("-w", "--width", default="5", help="width of the pipeline")
    parser.add_argument("-d", "--debug", action='store_true', help="Count of apps to launch")
    args   = parser.parse_args()

    if args.debug:
        pass
        parsl.set_stream_logger()

    #test_increment(depth=int(args.width))
    #test_increment(depth=int(args.width))
    test_increment_slow(depth=int(args.width))
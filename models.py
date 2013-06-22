import ghmm
import simplejson
import os.path

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
UP_RIGHT = 4
UP_LEFT = 5
DOWN_RIGHT = 6
DOWN_LEFT = 7
GESTES_COUNT = 4
OBSERVATIONS_COUNT = 8

gestures = [
    ([UP, RIGHT], ['/usr/bin/xdotool', 'getactivewindow', 'windowkill']),
    ([UP, LEFT], ['notify-send', '"received command"', '"Hooray!"']),
    ([DOWN], ['amixer', 'set', 'Master', '10%-']),
    ([UP], ['amixer', 'set', 'Master', '10%+']),
    ([UP, DOWN, UP], ['mplayer']),
]

training_data = [[] for gesture in gestures]

def uniq_list(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

# TODO: Zuordnung von Indizes stimmt noch nicht
def transition_matrix(gesture):
    gestes = uniq_list(gesture)
    A = [[0.1 for i in range(GESTES_COUNT)] for j in range(GESTES_COUNT)]
    # self transitions are high
    for geste in gestes:
        A[geste][geste] = 0.7

    first = gestes[0]

    for second in gestes[1:]:
        # if we have a transition, prob must be high
        A[first][second] = 0.3

    # ending element has no transitions anymore, so give it one
    A[gestes[-1]][gestes[-1]] = 1

    return A

def emission_matrix():
    B = [[float(1)/OBSERVATIONS_COUNT for i in range(OBSERVATIONS_COUNT)] for j in range(GESTES_COUNT)]
    
    B[UP] = [0.37, 0.04, 0.08, 0.08, 0.165, 0.165, 0.05, 0.05]
    B[DOWN] = [0.04, 0.37, 0.08, 0.08, 0.05, 0.05, 0.165, 0.165]
    B[LEFT] = [0.08, 0.08, 0.37, 0.04, 0.05, 0.165, 0.05, 0.165]
    B[RIGHT] = [0.08, 0.08, 0.04, 0.37, 0.165, 0.05, 0.165, 0.05]
    return B

def initial_vector(gesture):
    vec = [0 for i in range(GESTES_COUNT)]
    vec[gesture[0]] = 1
    return vec

# Construct parameters
models = []

sigma = ghmm.IntegerRange(0, 8)
i = 0
B = emission_matrix()
for gesture in gestures:
    A = transition_matrix(gesture[0])
    pi = initial_vector(gesture[0])
    
    m = ghmm.HMMFromMatrices(sigma, ghmm.DiscreteDistribution(sigma), A, B, pi)
    print(m)
    if os.path.isfile(''.join(('models/', str(i), '.train'))):
        with open(''.join(('models/', str(i), '.train'))) as f:
            training_data[i] = simplejson.load(f)
            m.baumWelch(ghmm.SequenceSet(sigma, training_data[i]))
    print(m)
    models.append((m, gesture[1]))

    i += 1

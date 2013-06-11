import ghmm

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
GESTES_COUNT = 4
OBSERVATIONS_COUNT = 4

gestures = [
    ([UP, RIGHT], ['/usr/bin/xdotool', 'getactivewindow', 'windowkill']),
    ([UP, LEFT], ['notify-send', '"received command"', '"Hooray!"']),
    ([DOWN], ['amixer', 'set', 'Master', '10%-']),
    ([UP], ['amixer', 'set', 'Master', '10%+']),
]

# TODO: Zuordnung von Indizes stimmt noch nicht
def transition_matrix(gesture):
    gestes = list(set(gesture))
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

def emission_matrix(gesture):
    gestes = set(gesture)
    B = [[0.1 for i in range(OBSERVATIONS_COUNT)] for j in range(GESTES_COUNT)]
    
    for geste in gestes:
        if geste == UP:
            B[geste] = [0.5, 0.1, 0.2, 0.2]
        elif geste == DOWN:
            B[geste] = [0.1, 0.5, 0.2, 0.2]
        elif geste == LEFT:
            B[geste] = [0.2, 0.2, 0.5, 0.1]
        else:
            B[geste] = [0.2, 0.2, 0.1, 0.5]

    return B

def initial_vector(gesture):
    vec = [0 for i in range(4)]
    vec[gesture[0]] = 1
    return vec

# Construct parameters
models = []

sigma = ghmm.IntegerRange(0, 4)
for gesture in gestures:
    # transition matrix
    A = transition_matrix(gesture[0])
    B = emission_matrix(gesture[0])
    pi = initial_vector(gesture[0])
                # in gesture
    m = ghmm.HMMFromMatrices(sigma, ghmm.DiscreteDistribution(sigma), A, B, pi)
    print(m)
    models.append((m, gesture[1]))

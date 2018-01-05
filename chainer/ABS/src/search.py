import numpy as np

def beamsearch(arguments, start, predFunc, beam_width, stop_id, max_length):

    length = 0
    yc = [start for _ in range(beam_width)]
    arguments = [arguments for _ in range(beam_width)]
    
    prob = predFunc(arguments, yc)
    choices= [[i] for i in np.argsort(prob[0])[-beam_width: ]]
    prob_choices = [p for p in np.sort(prob[0])[-beam_width: ]]
    yc = [yc_[1: ]+y_ for yc_, y_ in zip(yc, choices)]

    while length < max_length:
    #while length < 5:

        prob = predFunc(arguments, yc)
        temp_id = np.argsort(prob, axis=1)[:, -beam_width: ]
        temp_prob = np.sort(prob, axis=1)[:, -beam_width: ]

        temp_prob_choices = temp_prob * np.array(prob_choices)[:, np.newaxis]
        top_prob_indices = np.argsort(temp_prob_choices.flatten())[-1*beam_width: ]
        top_prob_indices = [(i//beam_width, i%beam_width) for i in top_prob_indices]
        
        choices = [choices[i]+[temp_id[i, j]] for i, j in top_prob_indices]
        prob_choices = [temp_prob_choices[i, j] for i, j in top_prob_indices]
        yc = [yc[i][1: ]+[temp_id.tolist()[i][j]] for i, j in top_prob_indices]

        length += 1

    return choices[-1]

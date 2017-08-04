import numpy
import pandas

import analysis
import parser

# Returns the probabilities of individual callers predicting a reportable variant
def get_indiv_weights(df):
    callers = parser.get_og_caller_names(df)
    weights = {}
    for caller in callers:
        tp = analysis.get_true_positives(df, caller).shape[0]
        fp = analysis.get_false_positives(df, caller).shape[0]
        tn = analysis.get_true_negatives(df, caller).shape[0]
        fn = analysis.get_false_negatives(df, caller).shape[0]
        all_calls = tp + fp + tn + fn
        weights[caller] = analysis.p_real_given_called(tp, fp, tp + fn, all_calls)
    return weights

# Returns true positive and false positive variants based on individual caller
# probabilities, with the cutoff as the dependent variable
def weight_fn(df, weights, cutoffs):
    callers = parser.get_og_caller_names(df)
    nps = [get_calls(df, weights, cutoff, 'P', 'N') for cutoff in cutoffs]
    #nps = [[
    #        'P' if sum([
    #                weight for k, weight in enumerate(weights) 
    #                if cov[callers[k]][i][1] == 'P'
    #        ]) > cutoff else 'N' for i in range(0, cov.shape[0])
    #] for cutoff in cutoffs]
    statuses = [[
            str((np[i] == 'P') == df['REPORTABLE'][i])[0] + np[i]
            for i in range(0, df.shape[0])
    ] for np in nps]
    tp = [len([s for s in status if s == 'TP']) for status in statuses]
    fp = [len([s for s in status if s == 'FP']) for status in statuses]
    tn = [len([s for s in status if s == 'TN']) for status in statuses]
    fn = [len([s for s in status if s == 'FN']) for status in statuses]
    return {'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn}

def get_calls(df, weights, cutoff, true_str, false_str):
    callers = parser.get_og_caller_names(df)
    return [true_str if sum([
                    weights[caller] for caller in callers
                    if df[caller][i][1] == 'P'
            ]) > cutoff else false_str for i in range(0, df.shape[0])
    ]

# Add a caller based on the probability of an individual caller correctly
# finding a reportable variant
def add_caller(df, training):
    callers = parser.get_og_caller_names(df)
    weights = get_indiv_weights(training)
    cutoffs = numpy.arange(0, sum([weights[c] for c in callers]), 0.01)
    vals = weight_fn(training, weights, cutoffs)
    mccs = [analysis.get_mcc(
            vals['TP'][i], vals['TN'][i], vals['FP'][i], vals['FN'][i]
    ) for i in range(0, len(vals['TP']))]
    cutoff = cutoffs[[i for i, mcc in enumerate(mccs) if mcc == max(mccs)][-1]]
    print('Individual cutoff: ' + str(cutoff))
    df['JOINT_INDIV'] = get_calls(df, weights, cutoff, True, './.')

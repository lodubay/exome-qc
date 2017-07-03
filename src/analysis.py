import pandas

# Reportable
def get_true_positives(df, caller_name):
    return df.iloc[[i for i, reportable in enumerate(df['REPORTABLE'])\
            if reportable and not df[caller_name][i] == './.']].reset_index(drop=True)

# Covered, not reportable
def get_false_positives(df, caller_name):
    return df.iloc[[i for i, covered in enumerate(df['COVERED'])\
            if covered and not df['REPORTABLE'][i]\
            and not df[caller_name][i] == './.']].reset_index(drop=True)

def get_false_negatives(tp, gt):
    return gt.iloc[[i for i in range(0, gt.shape[0])\
            if not (gt['GENE'][i] in tp['GENE'].tolist()\
            and gt['DNA_CHANGE'][i] in tp['DNA_CHANGE'].tolist()\
            and gt['PROTEIN_CHANGE'][i] in tp['PROTEIN_CHANGE'].tolist()
            and gt['SAMPLE_ID'][i] in tp['SAMPLE_ID'].tolist())]]\
            .reset_index(drop=True)

# Not covered, not reportable
def get_unclassified(df, caller_name):
    return df.iloc[[i for i, cov in enumerate(df['COVERED'])\
            if not cov and not df['REPORTABLE'][i]\
            and not df[caller_name][i] == './.']].reset_index(drop=True)

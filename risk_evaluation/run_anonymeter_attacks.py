import os
import pandas as pd
import json
from anonymeter.evaluators import InferenceEvaluator
from syndiffix import SyndiffixBlobReader

known_columns = [ 'CommToSch','CommHome','gender','age', 'DistFromHome','DistFromSchool']
secret_columns = ['VO2max', 'MVPAsqrt']
methods = { 'ARX': 'arx_syn.csv',
           'SDV': 'sdv_syn.csv',
           'SynDiffix': 'commute_anonymeter'}

# The original and control data are the same regardless of the anonymization method
script_dir = os.path.dirname(os.path.abspath(__file__))
origPath = os.path.join(script_dir, '..', 'CommDataOrig_original.csv')
df_orig = pd.read_csv(origPath, index_col=False)
df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]

controlPath = os.path.join(script_dir, '..', 'CommDataOrig_control.csv')
df_control = pd.read_csv(controlPath, index_col=False)
df_control = df_control.loc[:, ~df_control.columns.str.contains('^Unnamed')]
n_attacks = min(len(df_control), 1000)

sbr = SyndiffixBlobReader(blob_name=methods['SynDiffix'], path_to_dir=script_dir)

results = {}
for method in methods.keys():
    results[method] = {}
for secret in secret_columns:
    for method, file in methods.items():
        if method == 'SynDiffix':
            columns = known_columns + [secret]
            print(f"Reading SynDiffix table {columns}")
            df_syn = sbr.read(columns=columns)
        else:
            df_syn = pd.read_csv(os.path.join(script_dir, file), index_col=False)
        df_syn = df_syn.loc[:, ~df_syn.columns.str.contains('^Unnamed')]
        evaluator = InferenceEvaluator(ori=df_orig,
                                       syn=df_syn,
                                       control=df_control,
                                       aux_cols=known_columns,
                                       secret=secret,
                                       n_attacks=n_attacks,
                                       regression=True)
        evaluator.evaluate(n_jobs=-2)
        ev_risk = evaluator.risk()
        results[method][secret] = {'value': round(ev_risk.value, 3),
                                   'confidence_low': round(ev_risk.ci[0], 3),
                                   'confidence_high': round(ev_risk.ci[1], 3)}
        # Write results so far as json file
        with open(os.path.join(script_dir, 'results.json'), 'w') as f:
            json.dump(results, f, indent=4)
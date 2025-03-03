import json
import os
import subprocess

import anonymeter
import pandas as pd
import numpy
from anonymeter.evaluators import LinkabilityEvaluator, InferenceEvaluator, SinglingOutEvaluator
from anonymeter.stats.confidence import EvaluationResults, PrivacyRisk
from numpy.f2py.auxfuncs import throw_error
from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer
from sklearn.model_selection import train_test_split

from risk_evaluation.anonymeter_comparisons import attribute_inference_results_to_dataframe


def format_numbers_to_two_decimals(data):
    if isinstance(data, dict):
        return {key: format_numbers_to_two_decimals(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [format_numbers_to_two_decimals(item) for item in data]
    elif isinstance(data, (int, float)):
        return round(data, 2)
    else:
        return data


def results_to_dict(result: EvaluationResults):
    result = {
        "n_attacks": format_numbers_to_two_decimals(result.n_attacks),
        "n_success": format_numbers_to_two_decimals(result.n_success),
        "n_baseline": format_numbers_to_two_decimals(result.n_baseline),
        "n_control": format_numbers_to_two_decimals(result.n_control),
        "attack_rate": format_numbers_to_two_decimals(result.attack_rate._asdict()),
        "baseline_rate": format_numbers_to_two_decimals(result.baseline_rate._asdict()),
        "control_rate": format_numbers_to_two_decimals(result.control_rate._asdict()) if result.control_rate else None,
    }
    return result


def risk_to_dict(result: PrivacyRisk):
    _result = result._asdict()
    _result = {f"risk_{key}": value for key, value in _result.items()}
    return _result


def split_dataset(dataframe: pd.DataFrame,
                  fraction: float = .8,
                  seed: int = 387) -> (pd.DataFrame, pd.DataFrame):
    return train_test_split(dataframe, test_size=1 - fraction, random_state=seed)


def linkage_attack(synthetic, control, original, aux_columns):
    evaluator = LinkabilityEvaluator(ori=original, syn=synthetic, control=control, n_attacks=50,
                                     aux_cols=aux_columns, n_neighbors=1)

    evaluator.evaluate(n_jobs=-2)

    risk = risk_to_dict(evaluator.risk(confidence_level=0.95))
    results = results_to_dict(evaluator.results())
    return risk, results


def inference_attack(synthetic, holdout, df_original):
    columns = list(set(df_original.columns).intersection(synthetic.columns))
    results = []
    risks = []

    for secret in columns:
        aux_cols = [col for col in columns if col != secret]

        evaluator = InferenceEvaluator(ori=df_original.dropna(subset=aux_cols),
                                       syn=synthetic,
                                       control=holdout,
                                       aux_cols=aux_cols,
                                       secret=secret,
                                       n_attacks=50)
        evaluator.evaluate(n_jobs=-2)
        results.append((secret, results_to_dict(evaluator.results())))
        risks.append((secret, risk_to_dict(evaluator.risk())))
    return risks, results


def singlingout_attack(synthetic, holdout, df_original, mode="univariate"):
    evaluator = SinglingOutEvaluator(ori=df_original,
                                     syn=synthetic,
                                     control=holdout,
                                     n_attacks=50)
    evaluator.evaluate(mode=mode)
    risk = risk_to_dict(evaluator.risk(confidence_level=0.95))
    results = results_to_dict(evaluator.results())
    queries = evaluator.queries()
    return risk, results, queries


def export_results(anonymeter_results, output_file):
    with open(output_file + ".txt", 'a') as result_file:
        for run in anonymeter_results:
            result_file.write(str(run))
            result_file.write("\n")


def apply_anonymization(subset: pd.DataFrame) -> pd.DataFrame:
    """
    Executes a subprocess to anonymize the input file and saves the result in the output file
    """
    anon_input_file = "anon_input.csv"
    anon_output_file = "anon_output.csv"

    subset.to_csv(anon_input_file, index=None)

    if not os.path.isabs(anon_input_file):
        anon_input_file = os.path.join(os.getcwd(), anon_input_file.lstrip("./"))
    if not os.path.isabs(anon_output_file):
        anon_output_file = os.path.join(os.getcwd(), anon_output_file.lstrip("./"))

    repo_path = os.path.dirname(os.path.dirname(__file__))
    jar_location = os.path.join(repo_path, "ARX", "anonymize-commute-health-v0.1.jar")

    subprocess.run(["java",
                    "-jar", f"{jar_location}",
                    "-i", f"{anon_input_file}",
                    "-o", f"{anon_output_file}"])

    if not os.path.exists(anon_output_file):
        throw_error("Anonymization could not be performed.")

    result = pd.read_csv(anon_output_file)
    os.remove(anon_input_file)
    os.remove(anon_output_file)

    return result


def apply_sdv(df_orig: pd.DataFrame):
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df_orig)
    metadata.validate_data(data=df_orig)

    synthesizer = CTGANSynthesizer(metadata)
    synthesizer.fit(df_orig)

    df_syn = synthesizer.sample(num_rows=len(df_orig))
    return df_syn


def run_anonymeter_iteration(df_original, holdout, anonymized, available_columns, unavailable_columns):
    risk_inf, result_inf = inference_attack(anonymized, holdout, df_original)
    risk_link, result_link = linkage_attack(anonymized, holdout, df_original, [available_columns, unavailable_columns])
    risk_sout_uni, result_sout_uni, queries_uni = singlingout_attack(anonymized, holdout, df_original, "univariate")
    risk_sout_multi, result_sout_multi, queries_multi = singlingout_attack(anonymized, holdout, df_original, "multivariate")
    run_results = {
        "inference risk": risk_inf,
        "inference results": result_inf,
        "linkage health risk": risk_link,
        "linkage health results": result_link,
        "univariate Singling-out risk": risk_sout_uni,
        "univariate Singling-out results": result_sout_uni,
        "univariate Singling-out queries": queries_uni,
        "multivariate Singling-out risk": risk_sout_multi,
        "multivariate Singling-out results": result_sout_multi,
        "multivariate Singling-out queries": queries_multi
    }
    return run_results


def round_to_5(x):
    return 5 * round(x / 5)


if __name__ == "__main__":
    filename_original = r"../CommDataOrig.csv"

    df_original = pd.read_csv(filename_original)
    subset, holdout = split_dataset(df_original, fraction=.8)

    SELECTED_SPLIT = "80_20"


    # APPLY ARX/SynDiffix/SDV on subset
    anonymized = apply_anonymization(subset)
    synthetic = apply_sdv(subset)

    # Anonymeter configuration
    available_columns = ["CommHome", "CommToSch", "DistFromHome", "DistFromSchool"]
    unavailable_columns = ["MVPAsqrt", "VO2max", "age", "gender"]

    anonymeter_results = []
    inference_results = pd.DataFrame()
    for n in range(0, 20):
        print(f"Started iteration {n}")
        run_results = run_anonymeter_iteration(df_original, holdout, subset, available_columns, unavailable_columns)
        anonymeter_results.append(run_results)

    export_results(anonymeter_results, f"anonymeter_original_{SELECTED_SPLIT}")

    anonymeter_results = []
    for n in range(0, 20):
        print(f"Started arx iteration {n}")
        run_results = run_anonymeter_iteration(df_original, holdout, anonymized, available_columns, unavailable_columns)
        anonymeter_results.append(run_results)

    export_results(anonymeter_results, f"anonymeter_arx_{SELECTED_SPLIT}")

    anonymeter_results = []
    for n in range(0, 20):
        print(f"Started sdv iteration {n}")
        run_results = run_anonymeter_iteration(df_original, holdout, synthetic, available_columns, unavailable_columns)
        anonymeter_results.append(run_results)

    export_results(anonymeter_results, f"anonymeter_sdv_{SELECTED_SPLIT}")

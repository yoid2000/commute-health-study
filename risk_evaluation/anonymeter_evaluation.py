import anonymeter
import pandas as pd
import numpy
from anonymeter.evaluators import LinkabilityEvaluator, InferenceEvaluator, SinglingOutEvaluator
from sklearn.model_selection import train_test_split


def split_dataset(dataframe: pd.DataFrame,
                  fraction: float = .8,
                  seed: int = 387) -> (pd.DataFrame, pd.DataFrame):
    return train_test_split(dataframe, test_size=fraction, random_state=seed)


def linkage_attack(synthetic, control, original, aux_columns):
    evaluator = LinkabilityEvaluator(ori=original, syn=synthetic, control=control, n_attacks=400,
                                     aux_cols=aux_columns, n_neighbors=1)

    evaluator.evaluate(n_jobs=-2)

    risk = evaluator.risk(confidence_level=0.95)
    results = evaluator.results()
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
                                       n_attacks=100)
        evaluator.evaluate(n_jobs=-2)
        results.append((secret, evaluator.results()))
        risks.append((secret, evaluator.risk()))
    return risks, results


def singlingout_attack(synthetic, holdout, df_original, mode="univariate"):

    evaluator = SinglingOutEvaluator(ori=df_original,
                                     syn=synthetic,
                                     control=holdout,
                                     n_attacks=400)
    evaluator.evaluate(mode=mode)
    risk = evaluator.risk(confidence_level=0.95)
    results = evaluator.results()
    return risk, results


def export_results(anonymeter_results):
    for run in anonymeter_results:
        print(run)


if __name__ == "__main__":
    filename_original = r"../CommData.csv"

    df_original = pd.read_csv(filename_original)
    subset, holdout = split_dataset(df_original)

    # APPLY ARX/SynDiffix/SDV on subset
    synthetic = subset

    # Anonymeter configuration
    available_columns = ["CommHome", "CommToSch", "DistFromHome", "DistFromSchool"]
    unavailable_columns = ["MVPAsqrt", "VO2max", "age", "gender"]

    anonymeter_results = []
    for n in range(0, 10):
        print(f"Started iteration {n}")
        risk_inf, result_inf = inference_attack(synthetic, holdout, df_original)
        risk_link, result_link = linkage_attack(synthetic, holdout, df_original, [available_columns, unavailable_columns])
        risk_sout_uni, result_sout_uni = singlingout_attack(synthetic, holdout, df_original, "univariate")
        risk_sout_multi, result_sout_multi = singlingout_attack(synthetic, holdout, df_original, "multivariate")

        run_results = {
            "inference risk": risk_inf,
            "inference results": result_inf,
            "linkage health risk": risk_link,
            "linkage health results": result_link,
            "univariate Singling-out risk": risk_sout_uni,
            "univariate Singling-out results": result_sout_uni,
            "multivariate Singling-out risk": risk_sout_multi,
            "multivariate Singling-out results": result_sout_multi
        }
        anonymeter_results.append(run_results)

    export_results(anonymeter_results)

import pandas as pd


def import_results(input_file):
    try:
        with open(input_file, 'r') as result_file:
            # Read each line, stripping newline characters and converting back to appropriate data types
            results = [eval(line.strip()) for line in result_file]
        return results
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        return []
    except Exception as e:
        print(f"An error occurred while importing results: {e}")
        return []


def attribute_inference_results_to_dataframe(risk_df, result_df, iteration, split_type):
    _inf_df = pd.DataFrame(risk_df)
    _inf_df.columns = ["attribute", "risk_result"]
    _inf_df["iteration"] = iteration + 1
    _inf_df["split"] = split_type
    _inf_df['risk_value'] = _inf_df["risk_result"].apply(lambda x: x['risk_value'])
    _inf_df['risk_ci_low'] = _inf_df["risk_result"].apply(lambda x: x['risk_ci'][0])
    _inf_df['risk_ci_high'] = _inf_df["risk_result"].apply(lambda x: x['risk_ci'][1])
    _inf_df = _inf_df.drop("risk_result", axis=1)
    _inf_df = _inf_df.sort_values("attribute", key=lambda x: x.str.lower())

    _inf_res_df = pd.DataFrame(result_df)
    _inf_res_df.columns = ["attribute", "risk_result"]
    _inf_res_df['n_attacks'] = _inf_res_df["risk_result"].apply(lambda x: x['n_attacks'])
    _inf_res_df['n_success'] = _inf_res_df["risk_result"].apply(lambda x: x['n_success'])
    _inf_res_df['n_baseline'] = _inf_res_df["risk_result"].apply(lambda x: x['n_baseline'])
    _inf_res_df['n_control'] = _inf_res_df["risk_result"].apply(lambda x: x['n_control'])
    _inf_res_df['attack_rate_value'] = _inf_res_df["risk_result"].apply(lambda x: x['attack_rate']["value"])
    _inf_res_df['attack_rate_error'] = _inf_res_df["risk_result"].apply(lambda x: x['attack_rate']["error"])
    _inf_res_df['baseline_rate_value'] = _inf_res_df["risk_result"].apply(lambda x: x['baseline_rate']["value"])
    _inf_res_df['baseline_rate_error'] = _inf_res_df["risk_result"].apply(lambda x: x['baseline_rate']["error"])
    _inf_res_df['control_rate_value'] = _inf_res_df["risk_result"].apply(lambda x: x['control_rate']["value"])
    _inf_res_df['control_rate_error'] = _inf_res_df["risk_result"].apply(lambda x: x['control_rate']["error"])
    _inf_res_df = _inf_res_df.drop("risk_result", axis=1)
    _inf_res_df = _inf_res_df.sort_values("attribute", key=lambda x: x.str.lower())
    attribute_inference_df = pd.merge(_inf_df, _inf_res_df, on="attribute")
    return attribute_inference_df


def singlingout_results_to_dataframe(risk_list, result_list, split_type):
    sout_uni_risks = pd.DataFrame(risk_list)
    sout_uni_risks['risk_ci_low'] = sout_uni_risks["risk_ci"].apply(lambda x: x[0])
    sout_uni_risks['risk_ci_high'] = sout_uni_risks["risk_ci"].apply(lambda x: x[1])
    sout_uni_risks['iteration'] = sout_uni_risks.index
    sout_uni_risks["split"] = split_type

    sout_uni_results = pd.DataFrame(result_list)
    sout_uni_results['attack_rate_value'] = sout_uni_results["attack_rate"].apply(lambda x: x["value"])
    sout_uni_results['attack_rate_error'] = sout_uni_results["attack_rate"].apply(lambda x: x["error"])
    sout_uni_results['baseline_rate_value'] = sout_uni_results["baseline_rate"].apply(lambda x: x["value"])
    sout_uni_results['baseline_rate_error'] = sout_uni_results["baseline_rate"].apply(lambda x: x["error"])
    sout_uni_results['control_rate_value'] = sout_uni_results["control_rate"].apply(lambda x: x["value"])
    sout_uni_results['control_rate_error'] = sout_uni_results["control_rate"].apply(lambda x: x["error"])
    _temp = pd.concat([sout_uni_risks, sout_uni_results], axis=1)
    return _temp


if __name__ == "__main__":
    list_files = {
        "50_50": "anonymeter_original_50_50.txt",
        "70_30": "anonymeter_original_70_30.txt",
        "80_20": "anonymeter_original_80_20.txt",
        "90_10": "anonymeter_original_90_10.txt",
        "50_50_syn": "anonymeter_sdv_50_50.txt",
        "70_30_syn": "anonymeter_sdv_70_30.txt",
        "80_20_syn": "anonymeter_sdv_80_20.txt",
        "90_10_syn": "anonymeter_sdv_90_10.txt",
        "50_50_anon": "anonymeter_arx_50_50.txt",
        "70_30_anon": "anonymeter_arx_70_30.txt",
        "80_20_anon": "anonymeter_arx_80_20.txt",
        "90_10_anon": "anonymeter_arx_90_10.txt",
    }

    data = {}
    for key, value in list_files.items():
        data[key] = import_results(value)

    singlingout_uni_results = pd.DataFrame()
    singlingout_multi_results = pd.DataFrame()
    linkage_results = pd.DataFrame()
    inference_results = pd.DataFrame()
    for split_type in data.keys():
        _iterations = data[split_type]

        _temp = singlingout_results_to_dataframe([x["univariate Singling-out risk"] for x in _iterations],
                                         [x["univariate Singling-out results"] for x in _iterations],
                                         split_type)
        singlingout_uni_results = pd.concat([singlingout_uni_results, _temp], axis=0)
        del _temp

        _temp = singlingout_results_to_dataframe([x["multivariate Singling-out risk"] for x in _iterations],
                                         [x["multivariate Singling-out results"] for x in _iterations],
                                         split_type)
        singlingout_multi_results = pd.concat([singlingout_multi_results, _temp], axis=0)

        _temp = singlingout_results_to_dataframe([x["linkage health risk"] for x in _iterations],
                                         [x["linkage health results"] for x in _iterations],
                                         split_type)
        linkage_results = pd.concat([linkage_results, _temp], axis=0)

        for n in range(0, 10):  # len(_iterations)):
            attribute_inference_df = attribute_inference_results_to_dataframe(_iterations[n]["inference risk"],
                                                             _iterations[n]["inference results"],
                                                             n, split_type)
            inference_results = pd.concat([inference_results, attribute_inference_df], axis=0)

    statistics_inf = inference_results.groupby(["split", "attribute"])["risk_value"].describe()
    statistics_inf.to_csv("attribute_inference_risk_statistics.csv")

    statistics_sout_uni = singlingout_uni_results.groupby(["split"])["risk_value"].describe()
    statistics_sout_uni.to_csv("univariate_singlingout_risk_statistics.csv")

    statistics_sout_multi = singlingout_multi_results.groupby(["split"])["risk_value"].describe()
    statistics_sout_multi.to_csv("multivariate_singlingout_risk_statistics.csv")

    statistics_linkage = linkage_results.groupby(["split"])["risk_value"].describe()
    statistics_linkage.to_csv("linkage_risk_statistics.csv")

    print()

    # attribute_inferences
    # linkage
    # singlingout_uni
    # singlingout_multi

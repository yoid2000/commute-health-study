import json

# Load results.json into a dictionary
with open('results.json', 'r') as f:
    results = json.load(f)

# Open the output file in write mode
with open('risk_results.tex', 'w') as f:
    # Write the LaTeX table to the file
    f.write("\\begin{table}\n")
    f.write("\\begin{center}\n")
    f.write("\\begin{small}\n")
    f.write("\\begin{tabular}{rcccc}\n")
    f.write("\\toprule\n")
    f.write("Method & \\multicolumn{2}{c}{VO2max} & \\multicolumn{2}{c}{MVPAsqrt} \\\\ \n")
    f.write(" & Risk & (CI low, CI high) & Risk & (CI low, CI high) \\\\ \n")
    f.write("\\midrule\n")
    for method, secret_results in results.items():
        f.write(method + ' & ')
        for secret, result in secret_results.items():
            f.write(f"{result['value']} & ({result['confidence_low']}, {result['confidence_high']}) & ")
        f.write("\\\\ \n")
    f.write("\\bottomrule\n")
    f.write("\\end{tabular}\n")
    f.write("\\end{small}\n")
    f.write("\\caption{Privacy risk scores and 95\\% confidence intervals. Any risk score below 0.5 can be regarded as having very strong anonymity.}\n")
    f.write("\\label{tab:risk_eval}\n")
    f.write("\\end{center}\n")
    f.write("\\end{table}\n")
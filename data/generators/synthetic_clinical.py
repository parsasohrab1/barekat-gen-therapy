import numpy as np
import pandas as pd
from scipy.stats import weibull_min


def generate_gene_therapy_data(n_patients: int = 300, n_genes: int = 25, seed: int = 42) -> pd.DataFrame:
    """
    تولید داده‌های سنتتیک برای کارآزمایی ژن درمانی.

    پارامترها:
        n_patients: تعداد بیماران
        n_genes: تعداد ژن‌های هدف
        seed: seed تصادفی برای تکرارپذیری

    بازگشت:
        دیتافریم با داده‌های پاسخ به ژن درمانی
    """
    np.random.seed(seed)

    age = np.random.normal(45, 15, n_patients)
    age = np.clip(age, 10, 80).astype(int)

    gender = np.random.choice(["Male", "Female"], n_patients)
    disease_severity = np.random.uniform(1, 10, n_patients)

    gene_expression: dict[str, np.ndarray] = {}
    for i in range(n_genes):
        expression = np.random.normal(5, 2, n_patients)
        expression = np.clip(expression, 0, 15)
        gene_expression[f"Gene_{i + 1}_Expr"] = np.round(expression, 3)

    target_genes = ["Gene_5", "Gene_12", "Gene_18"]

    mutation_status: dict[str, np.ndarray] = {}
    for gene in target_genes:
        mutation_prob = np.clip(disease_severity / 15, 0.1, 0.8)
        mutation_status[f"{gene}_Mutation"] = np.random.binomial(1, mutation_prob)

    hazard_ratio = np.ones(n_patients)
    hazard_ratio *= 1 + 0.05 * (age - 45) / 15
    hazard_ratio *= disease_severity / 5
    hazard_ratio *= 1 + 0.3 * mutation_status["Gene_5_Mutation"]
    hazard_ratio *= 1 + 0.2 * mutation_status["Gene_12_Mutation"]
    hazard_ratio *= 1 - 0.3 * (gene_expression["Gene_18_Expr"] / 8)

    survival_times = weibull_min.rvs(1.5, scale=30 / hazard_ratio, size=n_patients)
    survival_times = np.clip(survival_times, 0.1, 365)

    event_status = (survival_times < 180).astype(int)

    toxicity_level = np.random.gamma(2, 0.3, n_patients) * mutation_status["Gene_5_Mutation"]
    toxicity_level = np.clip(toxicity_level, 0, 4)

    cytokine_storm = np.random.binomial(1, 0.1 + 0.05 * toxicity_level)

    df = pd.DataFrame(
        {
            "Patient_ID": [f"GT_{str(i).zfill(4)}" for i in range(n_patients)],
            "Age": age,
            "Gender": gender,
            "Disease_Severity": np.round(disease_severity, 2),
            "Gene_5_Mutation": mutation_status["Gene_5_Mutation"],
            "Gene_12_Mutation": mutation_status["Gene_12_Mutation"],
            "Gene_18_Mutation": mutation_status["Gene_18_Mutation"],
            "Time_to_Recovery_days": np.round(survival_times, 1),
            "Event_Status": event_status,
            "Treatment_Response": event_status,
            "Toxicity_Level": np.round(toxicity_level, 2),
            "Cytokine_Storm": cytokine_storm,
        }
    )

    for gene, expr in gene_expression.items():
        df[gene] = expr

    return df


if __name__ == "__main__":
    gene_therapy_data = generate_gene_therapy_data(n_patients=500)

    print(f"تعداد بیماران: {len(gene_therapy_data)}")
    print("\nآمار پاسخ به درمان:")
    print(gene_therapy_data["Treatment_Response"].value_counts())
    print(f"\nمتوسط زمان بهبودی: {gene_therapy_data['Time_to_Recovery_days'].mean():.1f} روز")
    print("\nنمونه داده:")
    print(gene_therapy_data.head())

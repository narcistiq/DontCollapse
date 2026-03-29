import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output/master_fragility_with_explanations.csv")
df = df.sort_values(by="Fragility_Score", ascending=False)

colors = df["Risk_Category"].map({
    "CRITICAL": "red",
    "HIGH": "orange",
    "MODERATE": "yellow",
    "LOW": "green"
})

plt.figure(figsize=(10, 6))
plt.bar(df["Zone_Name"], df["Fragility_Score"], color=colors)

plt.title("Fragility Score by Zone")
plt.xlabel("Zone")
plt.ylabel("Fragility Score")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("output/fragility_chart.png")
print("Chart saved to output/fragility_chart.png")

print("\nRecommended Actions by Zone:")
print(df[["Zone_Name", "Recommended_Action"]])
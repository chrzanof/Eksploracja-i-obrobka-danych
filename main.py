import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from mdutils.mdutils import MdUtils

dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"]
data = pd.read_csv(dataset_url, names=columns, na_values="?")

data = data.drop_duplicates()

data.fillna(data.median(numeric_only=True), inplace=True)

data = data.dropna(axis=1, how='all')

scaler = StandardScaler()
minmax_scaler = MinMaxScaler()

numerical_cols = data.select_dtypes(include=[np.number]).columns

data_standardized = data.copy()
data_standardized[numerical_cols] = scaler.fit_transform(data[numerical_cols])

data_normalized = data.copy()
data_normalized[numerical_cols] = minmax_scaler.fit_transform(data[numerical_cols])

mdFile = MdUtils(file_name='README', title='Eksploracja Danych')

mdFile.new_header(level=1, title='Statystyki opisowe')
desc_stats = data.describe().to_markdown()
mdFile.new_paragraph(desc_stats)

def save_and_add_plot(data, plot_func, filename, title, xlabel, ylabel):
    plt.figure(figsize=(12, 6))
    plot_func(data)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(filename)
    plt.close()
    mdFile.new_header(level=2, title=title)
    mdFile.new_paragraph(f'![{title}]({filename})')

save_and_add_plot(
    data['age'],
    lambda d: sns.histplot(d, bins=20, kde=True),
    'histogram_age.png',
    'Rozkład wieku pacjentów',
    'Wiek',
    'Liczba pacjentów'
)
save_and_add_plot(
    data['chol'],
    lambda d: sns.boxplot(x=d),
    'boxplot_chol.png',
    'Wykres pudełkowy poziomu cholesterolu',
    'Poziom cholesterolu',
    ''
)

save_and_add_plot(
    data,
    lambda d: sns.scatterplot(x=d['age'], y=d['thalach'], hue=d['sex']),
    'scatter_age_thalach.png',
    'Wiek vs Maksymalne Tętno',
    'Wiek',
    'Maksymalne Tętno'
)

save_and_add_plot(
    data,
    lambda d: sns.scatterplot(x=d['chol'], y=d['trestbps'], hue=d['target']),
    'scatter_chol_trestbps.png',
    'Poziom Cholesterolu vs Ciśnienie Krwi',
    'Poziom Cholesterolu',
    'Ciśnienie Krwi'
)

plt.figure(figsize=(12, 6))
corr = data.corr(numeric_only=True)
sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Macierz korelacji")
plt.savefig("correlation_matrix.png")
plt.close()
mdFile.new_header(level=2, title='Macierz korelacji')
mdFile.new_paragraph('![Macierz korelacji](correlation_matrix.png)')

data_standardized.to_csv("data_standardized.csv", index=False)
data_normalized.to_csv("data_normalized.csv", index=False)

mdFile.create_md_file()

print("Proces eksploracji i obróbki danych zakończony. Pliki zapisane.")

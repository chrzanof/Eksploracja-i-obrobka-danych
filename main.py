import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from mdutils.mdutils import MdUtils

# 1. Pobranie danych
# Źródło: UCI Heart Disease Dataset
dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"]
data = pd.read_csv(dataset_url, names=columns, na_values="?")

# 2. Czyszczenie danych
# Usuwanie duplikatów
data = data.drop_duplicates()

# Uzupełnianie brakujących wartości
data.fillna(data.median(numeric_only=True), inplace=True)

# Usunięcie niepotrzebnych kolumn (jeśli istnieją całkowicie puste)
data = data.dropna(axis=1, how='all')

# 3. Standaryzacja i normalizacja
scaler = StandardScaler()
minmax_scaler = MinMaxScaler()

numerical_cols = data.select_dtypes(include=[np.number]).columns

data_standardized = data.copy()
data_standardized[numerical_cols] = scaler.fit_transform(data[numerical_cols])

data_normalized = data.copy()
data_normalized[numerical_cols] = minmax_scaler.fit_transform(data[numerical_cols])

# 4. Eksploracja danych
# Tworzenie obiektu raportu Markdown
mdFile = MdUtils(file_name='README', title='Eksploracja Danych')

# Dodawanie statystyk opisowych do raportu
mdFile.new_header(level=1, title='Statystyki opisowe')
desc_stats = data.describe().to_markdown()
mdFile.new_paragraph(desc_stats)

# Wykresy
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

# Histogram wieku pacjentów
save_and_add_plot(
    data['age'],
    lambda d: sns.histplot(d, bins=20, kde=True),
    'histogram_age.png',
    'Rozkład wieku pacjentów',
    'Wiek',
    'Liczba pacjentów'
)

# Wykres pudełkowy poziomu cholesterolu
save_and_add_plot(
    data['chol'],
    lambda d: sns.boxplot(x=d),
    'boxplot_chol.png',
    'Wykres pudełkowy poziomu cholesterolu',
    'Poziom cholesterolu',
    ''
)

# Wykres rozrzutu: wiek vs maksymalne tętno
save_and_add_plot(
    data,
    lambda d: sns.scatterplot(x=d['age'], y=d['thalach'], hue=d['sex']),
    'scatter_age_thalach.png',
    'Wiek vs Maksymalne Tętno',
    'Wiek',
    'Maksymalne Tętno'
)

# Wykres rozrzutu: poziom cholesterolu vs ciśnienie krwi
save_and_add_plot(
    data,
    lambda d: sns.scatterplot(x=d['chol'], y=d['trestbps'], hue=d['target']),
    'scatter_chol_trestbps.png',
    'Poziom Cholesterolu vs Ciśnienie Krwi',
    'Poziom Cholesterolu',
    'Ciśnienie Krwi'
)

# Macierz korelacji
plt.figure(figsize=(12, 6))
corr = data.corr(numeric_only=True)
sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Macierz korelacji")
plt.savefig("correlation_matrix.png")
plt.close()
mdFile.new_header(level=2, title='Macierz korelacji')
mdFile.new_paragraph('![Macierz korelacji](correlation_matrix.png)')

# 5. Dodatkowe analizy
# Histogramy dla innych zmiennych numerycznych
save_and_add_plot(
    data['trestbps'],
    lambda d: sns.histplot(d, bins=20, kde=True),
    'histogram_trestbps.png',
    'Rozkład ciśnienia krwi',
    'Ciśnienie Krwi',
    'Liczba pacjentów'
)

save_and_add_plot(
    data['oldpeak'],
    lambda d: sns.histplot(d, bins=20, kde=True),
    'histogram_oldpeak.png',
    'Rozkład depresji ST',
    'Depresja ST',
    'Liczba pacjentów'
)

# Wykres pudełkowy dla zmiennych kategorycznych (np. 'target' vs 'chol')
save_and_add_plot(
    data,
    lambda d: sns.boxplot(x=d['target'], y=d['chol']),
    'boxplot_target_chol.png',
    'Poziom cholesterolu vs target',
    'Target',
    'Poziom cholesterolu'
)

# Wykresy rozrzutu: Wiek vs cholesterol z uwzględnieniem 'target'
save_and_add_plot(
    data,
    lambda d: sns.scatterplot(x=d['age'], y=d['chol'], hue=d['target']),
    'scatter_age_chol_target.png',
    'Wiek vs Poziom Cholesterolu',
    'Wiek',
    'Poziom Cholesterolu'
)

# Macierz kontyngencji dla zmiennych kategorycznych
categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
for col in categorical_cols:
    contingency_table = pd.crosstab(data[col], data['target'])
    mdFile.new_header(level=2, title=f'Macierz kontyngencji dla {col} i target')
    mdFile.new_paragraph(contingency_table.to_markdown())

# Analiza outlierów
plt.figure(figsize=(12, 6))
sns.boxplot(data=data[numerical_cols])
plt.title('Analiza outlierów dla zmiennych numerycznych')
plt.savefig('outliers.png')
plt.close()
mdFile.new_header(level=2, title='Analiza Outlierów')
mdFile.new_paragraph('![Analiza Outlierów](outliers.png)')

# 6. Zapis przetworzonych danych
data_standardized.to_csv("data_standardized.csv", index=False)
data_normalized.to_csv("data_normalized.csv", index=False)

# Zapis raportu do pliku Markdown
mdFile.create_md_file()

print("Proces eksploracji i obróbki danych zakończony. Pliki zapisane.")

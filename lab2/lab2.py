import os
import urllib.request
import pandas as pd
from datetime import datetime


VHI_DIR = "vhi_data"

def download_vhi_data(region_id):
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{VHI_DIR}/vhi_{region_id}_{now}.csv"
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={region_id}&year1=1981&year2=2024&type=Mean"
    
    vhi_url = urllib.request.urlopen(url)
    with open(filename, 'wb') as file:
        file.write(vhi_url.read())
    
    print(f"VHI for region {region_id} is downloaded")

def load_vhi_data(folder_path):
    
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    csv_files = os.listdir(folder_path)
    csv_files = [f for f in csv_files if f.startswith("vhi_") and f.endswith(".csv")]
    csv_files.sort(key=lambda f: int(f.split("_")[1]))
    
    dataframes = []
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        region_id = int(file.split("_")[1])
        df = pd.read_csv(file_path, header=1, names=headers)
        df = df.drop(columns=['empty'], errors='ignore')
        df = df[df['VHI'] != -1]
        df['area'] = region_id
        dataframes.append(df)
    
    final_df = pd.concat(dataframes, ignore_index=True)
    return final_df

def rename_regions(df):
    
    region_mapping = {
        1: "Черкаська", 2: "Чернігівська", 3: "Чернівецька", 4: "Республіка Крим",
        5: "Дніпропетровська", 6: "Донецька", 7: "Івано-Франківська", 8: "Харківська",
        9: "Херсонська", 10: "Хмельницька", 11: "Київська", 12: "Київ",
        13: "Кіровоградська", 14: "Луганська", 15: "Львівська", 16: "Миколаївська",
        17: "Одеська", 18: "Полтавська", 19: "Рівненська", 20: "Севастопольська",
        21: "Сумська", 22: "Тернопільська", 23: "Закарпатська", 24: "Вінницька",
        25: "Волинська", 26: "Запорізька", 27: "Житомирська"
    }
    
    df["area"].replace(region_mapping, inplace=True)
    return df

def clean_year_column(df):
    
    df = df.copy()
    df["Year"] = df["Year"].astype(str).str.extract(r'(\d{4})')
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    return df

def get_vhi_for_region_year(df, region, year):
    
    df = clean_year_column(df)
    result = df[(df["area"] == region) & (df["Year"] == year)][['Week', 'VHI']]
    
    return result

def get_vhi_stats(df, region=None, year=None):
    
    df = clean_year_column(df)
    filtered_df = df[df["VHI"] != -1]  
    
    if region:
        filtered_df = filtered_df[filtered_df["area"] == region]
    if year:
        filtered_df = filtered_df[filtered_df["Year"] == year]
    
    if filtered_df.empty:
        return {"min": None, "max": None, "mean": None, "median": None}
    
    return {
        "min": filtered_df["VHI"].min(),
        "max": filtered_df["VHI"].max(),
        "mean": filtered_df["VHI"].mean(),
        "median": filtered_df["VHI"].median()
    }

def get_vhi_for_region_years(df, region, start_year, end_year):
    
    df = clean_year_column(df)
    result = df[(df["area"] == region) & (df["Year"].between(start_year, end_year))][['Year', 'Week', 'VHI']]
        
    return result

def get_extreme_drought_years(df, percentage_threshold=20):
    
    df = clean_year_column(df)
    total_regions = 27  
    min_regions = (percentage_threshold / 100) * total_regions  
    
    drought_df = df[df["VHI"] <= 15]
    drought_counts = drought_df.groupby("Year")["area"].nunique()
    
    extreme_drought_years = drought_counts[drought_counts >= min_regions].index.tolist()
    drought_details = df[(df["Year"].isin(extreme_drought_years)) & (df["VHI"] <= 15)][['Year', 'area', 'VHI']]
    
    return extreme_drought_years, drought_details

def main():
    
    os.makedirs(VHI_DIR, exist_ok=True)
    
   
    print("Починаємо завантаження даних для всіх областей України...")
    for region_id in range(1, 28):
        download_vhi_data(region_id)
    print("Завантаження даних завершено.")
    
   
    print("Об'єднання даних з усіх файлів...")
    final_dataframe = load_vhi_data(VHI_DIR)
    final_dataframe.to_csv("vhi_data.csv", index=False)
    print("Дані збережено у файл vhi_data.csv")
    
   
    print("Заміна ID областей на назви...")
    final_dataframe = rename_regions(final_dataframe)
    final_dataframe.to_csv("vhi_data_regions.csv", index=False)
    print("Дані з назвами областей збережено у файл vhi_data_regions.csv")
    
    
    print("Очищення даних...")
    clean_data = clean_year_column(final_dataframe)
    clean_data.to_csv("vhi_data_clean.csv", index=False)
    print("Очищені дані збережено у файл vhi_data_clean.csv")
    
    print("Обробка даних завершена успішно!")

if __name__ == "__main__":
    main()

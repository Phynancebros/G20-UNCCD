import pandas as pd
import matplotlib.pyplot as plt

def visualize_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        
        # Bar chart for AREA_SQKM
        plt.figure(figsize=(10, 6))
        plt.bar(df['ADM2_EN'], df['AREA_SQKM'], color='skyblue')
        plt.xlabel('Region')
        plt.ylabel('Area (sq km)')
        plt.title('Area of Regions in Assaba')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(csv_path.replace('.csv', '_area.png'))
        plt.show()
        
        # Bar chart for Shape_Area
        plt.figure(figsize=(10, 6))
        plt.bar(df['ADM2_EN'], df['Shape_Area'], color='lightgreen')
        plt.xlabel('Region')
        plt.ylabel('Shape Area')
        plt.title('Shape Area of Regions in Assaba')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(csv_path.replace('.csv', '_shape_area.png'))
        plt.show()
        
    except Exception as e:
        print(f"Error visualizing data from {csv_path}: {e}")

if __name__ == "__main__":
    csv_path = 'Datasets_Hackathon/Admin_layers/Assaba_Region_layer.csv'
    visualize_data(csv_path)

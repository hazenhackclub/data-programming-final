
import geopandas as gpd
import matplotlib.pyplot as plt

def import_geodata(filename):
    return gpd.open_csv(filename)

def main():
    print(import_geodata('test'))

if __name__ == "__main__":
    main()

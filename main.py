from load_data import load_data, Country, scatter_plot_from_coordinates, plot_world
import pdb
import matplotlib.pyplot as plt
import math


def main():
    data_set_path = 'world-administrative-boundaries.json'
    data_set = load_data(data_set_path)

    countries = []
    for i, c in enumerate(data_set):
        country = Country.from_dict(c)

        countries.append(country)

    plot_world(countries)


if __name__ == "__main__":
    main()
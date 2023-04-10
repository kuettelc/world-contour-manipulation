from load_data import load_data, Country, plot_world


def main():
    data_set_path = 'world-administrative-boundaries.json'
    data_set = load_data(data_set_path)

    countries = []
    for i, c in enumerate(data_set):
        country = Country.from_dict(c)

        countries.append(country)

    plot_world(countries, area_lower_bound=1.0)


if __name__ == "__main__":
    main()
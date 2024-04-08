from flask import Flask, jsonify, request
import csv
import cities
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

cities_data_fin = {}
cityList = []

qualityNormalized = []
safetyNormalized = []
employabilityNormalized = []


def load_data():
    import csv
    f = open('./data/city_education_crime_employment_homeprice.csv', encoding='utf-8')
    raw_data = list(csv.reader(f))
    f.close()
    header = raw_data[0]
    header.pop(0)
    raw_data = raw_data[1:]
    for data in raw_data:
        data.pop(0)
        value = {}
        for i in range(len(header)):
            value[header[i]] = data[i]
        for stat in value:
            # print(stat)
            if stat in ['population', 'average_education_index', 'crime_index,sixteen_plus_employed_percentage',
                        'house_median_value', 'edu_index_norm,employed_percentage_norm']:
                # print(int(pkmn[stat]))
                value[stat] = float(value[stat])
        cities_data_fin[value["city"]] = value


def get_city_name(city):
    return cities_data_fin[city]["city"]


def get_city_population(city):
    return cities_data_fin[city]["population"]


def get_average_education_index(city):
    return cities_data_fin[city]["average_education_index"]


def get_crime(city):
    return cities_data_fin[city]["crime_index"]


def get_price(city):
    return cities_data_fin[city]["house_median_value"]


def get_employment(city):
    return cities_data_fin[city]["sixteen_plus_employed_percentage"]


def get_edu_norm(city):
    return cities_data_fin[city]["edu_index_norm"]


def get_employed_norm(city):
    return cities_data_fin[city]["employed_percentage_norm"]


def makeArrays():
    global qualityNormalized, safetyNormalized, employabilityNormalized
    for city in cities_data_fin:
        qualityNormalized.append(get_average_education_index(city))
        safetyNormalized.append(get_crime(city))
        employabilityNormalized.append(get_employed_norm(city))
        cityList.append(get_city_name(city))


def get_city(city):
    return cities.cities[city]


@app.route("/filter_data", methods=["GET"])
def filter():
    """
    This function filters the cities based on the user's input
    :param user_employability: A ranking 1-5 of how important employability is to the user
    :param user_safety: A ranking 1-5 of how important safety is to the user
    :param user_quality: A ranking 1-5 of how important quality is to the user
    :param user_budget: The user's budget
    :return: A JSON list of cities sorted by the user's preferences
    """
    load_data()
    makeArrays()
    # return jsonify(cities_data_fin)
    # return jsonify(get_employment("Madison"))

    global cityList, qualityNormalized, safetyNormalized, employabilityNormalized

    user_employability = int(request.args.get("user_employability", default=None))
    user_safety = int(request.args.get("user_safety", default=None))
    user_quality = int(request.args.get("user_quality", default=None))
    user_budget = float(request.args.get("user_budget", default=None))

    if user_employability is None or user_safety is None or user_quality is None or user_budget is None:
        return jsonify({"error": "Missing required parameters"})\

    if user_employability < 1 or user_employability > 5 or user_safety < 1 or user_safety > 5 or user_quality < 1 or user_quality > 5 or user_budget < 0:
        return jsonify({"error": "Invalid parameters"})
    # Filter cities based on user budget
    filtered_cities = [city for city in cities_data_fin.values() if city["house_median_value"] <= user_budget]

    # Uses list comprehension to fill in the modified ratings
    modified_quality = [float(city_quality_ranking_normalized) * user_quality for city_quality_ranking_normalized in
                        qualityNormalized]
    modified_safety = [float(city_safety_ranking_normalized) * user_safety/1000 for city_safety_ranking_normalized in
                       safetyNormalized]  # /1000 because user_safety was weirdly high
    modified_employability = [float(city_employability_ranking_normalized) * user_employability for
                              city_employability_ranking_normalized in employabilityNormalized]

    # Combine modified ratings
    combined_rating = [float(quality_ranking) + float(safety_ranking) + float(employability_ranking) for
                       quality_ranking, safety_ranking, employability_ranking in
                    zip(modified_quality, modified_safety, modified_employability)]

    # print(combined_rating)
    # print([city['city']for city in filtered_cities])

    city_rating_pairs = list(zip(filtered_cities, combined_rating))
    city_rating_pairs.sort(key=lambda pair: pair[1], reverse=True)
    sorted_cities = [pair[0] for pair in city_rating_pairs]

    return jsonify(sorted_cities)


if __name__ == "__main__":
    app.run()

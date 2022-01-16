import argparse
import bicimad
import pandas as pd


def _generate_relevant_df(data):
    relevant_cols = [
        "organization.organization-name",
        "Tipo_Centro",
        "address.street-address",
        "bici_name",
        "bici_address",
        "bici_dist_total",
    ]
    data = data[relevant_cols]
    data = data.rename(
        columns={
            "organization.organization-name": "place_name",
            "Tipo_Centro": "place_type",
            "address.street-address": "place_address",
            "bici_name": "bicimad_estation",
            "bici_address": "station_location",
            "bici_dist_total": "distance",
        }
    )
    return data


def get_closest_bike_to_all():
    org_data = bicimad.load_data_organizaciones()
    bike_data = bicimad.load_data_bicis()
    # this returns a dataframe
    org_data[
        [
            "bici_name",
            "bici_address",
            "bici_lat",
            "bici_lon",
            "bici_coordinadas_mercator",
            "bici_dist_total",
        ]
    ] = org_data.apply(lambda x: bicimad.get_closest_bike(x, bike_data.copy()), axis=1)
    # need to narrow it down to relevant columns
    relevant_df = _generate_relevant_df(org_data)
    return relevant_df


def get_closest_bike_to_location(org_name, fuzzy):
    location_data = bicimad.find_organization_by_name(org_name, fuzzy)
    if location_data is None:
        # if org wasn't found, exit
        return
    bike_data = bicimad.load_data_bicis()
    # this returns a dictionary
    closest_bike = bicimad.get_closest_bike(location_data, bike_data.copy())
    # combine both dictionaries
    location_data["bici_name"] = closest_bike["name"]
    location_data["bici_address"] = closest_bike["address"]
    location_data["bici_dist_total"] = closest_bike["distancia_total"]
    # convert to dataframe of a single row
    enriched_data = pd.DataFrame([location_data])
    # need to narrow it down to relevant columns
    relevant_df = _generate_relevant_df(enriched_data)
    return relevant_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--action",
        help="Define what you want to do.",
        choices=["closest-bike-location", "closest-bike-all"],
        required=True,
    )

    parser.add_argument(
        "--organization-name",
        help="Provide the org name.",
        dest="org_name",
    )

    parser.add_argument(
        "--output-format",
        help="Choose how to generate the data.",
        choices=["print", "csv"],
        dest="output_format",
        required=True,
    )

    parser.add_argument(
        "--fuzzy",
        help="Set flag if searching for location using fuzzy match",
        action="store_true",
    )

    args = parser.parse_args()
    if args.action == "closest-bike-all":
        data = get_closest_bike_to_all()
        suffix = "all"
    elif args.action == "closest-bike-location":
        data = get_closest_bike_to_location(args.org_name, args.fuzzy)
        suffix = args.org_name
    # since an organization may not be found, we need to check if data isn't empty
    if data is not None:
        # write results
        if args.output_format == "csv":
            # this format just replaces brackets with variable values
            filename = "./output_files/{}-{}.csv".format(args.action, suffix)
            data.to_csv(filename)
            print("The output file has been generated under {}".format(filename))
        else:
            # print to screen
            print(data.to_markdown())

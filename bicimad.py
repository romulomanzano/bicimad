import pandas as pd
import requests
import geo_calculations as geo
from fuzzywuzzy import fuzz


def _load_cc():
    """
    Internal function to return centros culturales
    returns: pandas dataframe
    """
    centros_culturales = requests.get(
        "https://datos.madrid.es/egob/catalogo/200304-0-centros-culturales.json"
    )
    centros_culturales = centros_culturales.json()
    df_centros_culturales = pd.json_normalize(centros_culturales["@graph"])
    df_centros_culturales = pd.DataFrame(
        df_centros_culturales[
            [
                "organization.organization-name",
                "address.street-address",
                "location.latitude",
                "location.longitude",
            ]
        ]
    )
    df_centros_culturales = df_centros_culturales.assign(
        Tipo_Centro="Centros culturales"
    )
    return df_centros_culturales


def _load_museos():
    """
    Internal function to return museums
    returns: pandas dataframe
    """
    museos = requests.get("https://datos.madrid.es/egob/catalogo/201132-0-museos.json")
    museos = museos.json()
    df_museos = pd.json_normalize(museos["@graph"])
    df_museos = pd.DataFrame(
        df_museos[
            [
                "organization.organization-name",
                "address.street-address",
                "location.latitude",
                "location.longitude",
            ]
        ]
    )
    df_museos = df_museos.assign(Tipo_Centro="Museos")
    return df_museos


def load_data_organizaciones():
    data = pd.concat([_load_cc(), _load_museos()])
    # calculate mercator coordinates
    data["coordinadas_mercator"] = data.apply(
        lambda x: geo.to_mercator(x["location.latitude"], x["location.longitude"]),
        axis=1,
    )
    return data


def find_organization_by_name(org_name, fuzzy):
    # returns a dictionary
    data = load_data_organizaciones()
    if not fuzzy:
        # simple search
        try:
            org = data[data["organization.organization-name"] == org_name].iloc[0]
            return org
        except Exception as e:
            print("Organization not found!")
            return None
    else:  # if fuzzy
        data["fuzzy_ratio"] = data.apply(
            lambda x: fuzz.token_sort_ratio(
                x["organization.organization-name"], org_name
            ),
            axis=1,
        )
        # consider a match if ratio score is >80, see: https://pypi.org/project/fuzzywuzzy/
        matched = data[data["fuzzy_ratio"] > 80]
        if not matched.empty:
            print(
                "{} organizations found using fuzzy match with close enough names".format(
                    len(matched)
                )
            )
            return matched.sort_values(by="fuzzy_ratio", ascending=False).iloc[0]
        else:
            print("No organization found using fuzzy match!")
            return None


def load_data_bicis():
    """
    Internal function to return bici data
    returns: pandas dataframe
    """
    df_bicimadstations = pd.read_json("./data/bicimadstations.json")
    # aca tenian un bug grave, estaban asugnando longitud a latitud y viceversa
    lon = [
        float(index["geometry_coordinates"].split(",")[0].replace("[", ""))
        for row, index in df_bicimadstations.iterrows()
    ]
    lat = [
        float(index["geometry_coordinates"].split(",")[1].replace("]", ""))
        for row, index in df_bicimadstations.iterrows()
    ]
    df_bicimadstations["latitud"] = lat
    df_bicimadstations["longitud"] = lon
    df_bicimadstations = pd.DataFrame(
        df_bicimadstations[["name", "address", "latitud", "longitud"]]
    )
    # notar que he utilizado la funcion del modulo `geo_calculations`, el cual importe como "geo"
    df_bicimadstations["coordinadas_mercator"] = df_bicimadstations.apply(
        lambda x: geo.to_mercator(x["latitud"], x["longitud"]), axis=1
    )
    return df_bicimadstations


def get_closest_bike(data_lugar, df_bicis):
    """
    Args:
        data_lugar: un diccionario/objecto con el museo/centro
        df_bicis: un dataframe con la data de bicimadrid
    """
    df_bicis["distancia_total"] = df_bicis.apply(
        lambda x: x["coordinadas_mercator"].distance(
            data_lugar["coordinadas_mercator"]
        ),
        axis=1,
    )
    return df_bicis.sort_values(by="distancia_total", ascending=True).iloc[0]

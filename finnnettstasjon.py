import math
#from arcgis.gis import GIS
#from arcgis.features import FeatureLayer
#from arcgis.geometry import Geometry
import configparser
import requests
import regex as re
import pandas as pd
# Lag config parser object
config = configparser.ConfigParser()


#listid = "6f184afe-6252-421a-83c8-bd9c7d89ceb4" #test
listid = 'e1473d92-bbf4-49bd-86a2-18112e3bbd71' #prod

#siteid = "14f6ef1e-61d5-41a5-b7b8-2ffc10278e77" #test
siteid = 'fcad0319-3f58-4eeb-a3ac-d67248d48d93' #prod

# Les config filen
config.read('config.ini')

def get_sharepoint_token():
    # Dine Azure AD applikasjonsdetaljer
    client_id = config['sharepoint']['client_id']  # Bytt ut med din Client ID
    client_secret = config['sharepoint']['client_secret']  # Bytt ut med din Client Secret
    tenant_id = config['sharepoint']['tenant_id'] # Bytt ut med din Tenant ID

    # URL for å få tilgangstoken fra Azure AD
    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

    # Data for å få tilgangstoken
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }

    # Send forespørselen for å få tilgangstoken
    token_response = requests.post(token_url, data=token_data)
    token_response.raise_for_status()  # Sjekk for feil i forespørselen
    token = token_response.json().get('access_token')

    return token


token = get_sharepoint_token()  # Kjør funksjonen for å hente tilgangstoken

def get_sharepoint_trafos():
    site_id = siteid  # Bytt ut med ditt Site ID (du kan finne dette via Graph API)
    list_id = listid  # Bytt ut med ID eller navnet på SharePoint-listen

    graph_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/columns"

    # Headers for å autorisere forespørselen
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(graph_url, headers=headers)
    
    # Sjekk om forespørselen var vellykket
    if response.status_code == 200:
        columns = response.json()['value']
        for column in columns:
            if column['name'] == 'Trafostasjon':  # Bytt ut med riktig felt for Multiple Choice
                # Hent ut valgene fra feltet 'choice'
                choices = column.get('choice', {}).get('choices', [])
                print(f"Valg i 'Trafostasjon': {choices}")
                return choices
    else:
        print(f"Feil ved forespørsel: {response.status_code}, {response.text}")


# Funksjon for å hente data fra SharePoint-listen
def get_sharepoint_list():
    # SharePoint-spesifikke detaljer
    site_id = siteid  # Bytt ut med ditt Site ID (du kan finne dette via Graph API)
    list_id = listid  # Bytt ut med ID eller navnet på SharePoint-listen

    graph_api_endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items?expand=fields'

    # Headers for å autorisere forespørselen
    headers = {
        'Authorization': f'Bearer {token}'
    }
    items = []

    while graph_api_endpoint:
        # Send forespørselen til Microsoft Graph API
        response = requests.get(graph_api_endpoint, headers=headers)
        response.raise_for_status()  # Sjekk for feil i forespørselen

        # Hent data fra SharePoint-listen
        data = response.json()

        # Kontroller at 'value' finnes i responsen, som er forventet å være en liste
        if 'value' in data:
            items.extend(data['value'])
        else:
            print("No 'value' key found in the response.")
            break

        # Sjekk om det er flere sider med data
        graph_api_endpoint = data.get('@odata.nextLink')
    

    print(f"Antall elementer hentet: {len(items)}")

    return items

# Funksjon for å beregne avstand ved hjelp av Haversine-formelen
def haversine_distance(lon1, lat1, lon2, lat2):
    R = 6371000  # Radiusen av jorden i meter
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Avstand i meter

def calculate_distance(feature, point):
        feature_x = feature.geometry['x']
        feature_y = feature.geometry['y']
        point_x = point['x']
        point_y = point['y']
        
        # Skriv ut begge punktene for feilsøking
        #print(f"Funksjon: {feature.geometry}")
        #print(f"Søkepunkt: {point}")

        # Beregn avstanden ved hjelp av Haversine-formelen
        distance = haversine_distance(point_x, point_y, feature_x, feature_y)
        #print(f"Distanse: {distance}")  # Skriv ut avstanden for å se om den blir beregnet
        return distance

""" def get_arcgis_lag():
    username = config['arcgis']['username']
    password = config['arcgis']['password']

    # Logg inn på ArcGIS Online eller Enterprise
    gis = GIS("https://www.arcgis.com", username, password)

    # Alternativt hvis du bruker Enterprise
    # gis = GIS("https://<your-enterprise-server-url>", "username", "password")
    # Nå er du logget inn og kan gjøre forespørsler
    # URL-en til ArcGIS-laget
    layer_url = "https://utility.arcgis.com/usrsvcs/servers/1b1ce6064f284661881cf14fe41dd6d7/rest/services/Powel/iAMViewer3/MapServer/0"

    # Lag en FeatureLayer-objekt
    feature_layer = FeatureLayer(layer_url)

    print("Feature layer loaded")
    print(feature_layer.properties.name)

    return feature_layer """

def find_closest( lon, lat):

    """ username = config['arcgis']['username']
    password = config['arcgis']['password']

    # Logg inn på ArcGIS Online eller Enterprise
    gis = GIS("https://www.arcgis.com", username, password)

    # Alternativt hvis du bruker Enterprise
    # gis = GIS("https://<your-enterprise-server-url>", "username", "password")
    # Nå er du logget inn og kan gjøre forespørsler
    # URL-en til ArcGIS-laget
    layer_url = "https://utility.arcgis.com/usrsvcs/servers/1b1ce6064f284661881cf14fe41dd6d7/rest/services/Powel/iAMViewer3/MapServer/0"

    # Lag en FeatureLayer-objekt
    feature_layer = FeatureLayer(layer_url) """

    print("Feature layer loaded")
    print(feature_layer.properties.name)

    # Definer punktet du vil søke fra (din koordinat i WGS 84)
    point = Geometry({
        "x": lon,
        "y": lat,
        "spatialReference": {"wkid": 4326}
    })

    print(f"Søkepunkt: {point}")

    # Utfør en spørring for å finne funksjoner innenfor et bestemt område (10 000 meter)
    result = feature_layer.query(where="1=1",out_sr=4326)

    print(f"Antall funksjoner: {len(result.features)}") 

    """ for feature in result.features:
        print(f"Funksjon: {feature.geometry}")
        distanse = calculate_distance(feature, point)
        print(f"Distanse: {distanse}") """


    # Filtrer bort funksjoner som har 'None' som geometri eller mangler 'x' og 'y' koordinater
    valid_features = [f for f in result.features if f.geometry is not None and 'x' in f.geometry and 'y' in f.geometry and f.attributes['OBJECTID'] != 21]

    # Hvis det er gyldige funksjoner, finn den nærmeste
    if valid_features:
        # Konverter hver funksjonens geometri til Geometry-objekt og beregn avstand, med sjekk for None
        
        # Finn den nærmeste funksjonen som ikke returnerer None for avstand
        nearest_feature = min(valid_features, key=lambda f: calculate_distance(f, point) if calculate_distance(f, point) is not None else float('inf'))
        # Beregn distansen til det nærmeste punktet
        nearest_distance = calculate_distance(nearest_feature, point)
        # Skriv ut resultatene
        print(f"Den nærmeste funksjonen er: {nearest_feature}")
        print(f"Distansen til den nærmeste funksjonen er: {nearest_distance} meter")
        
        # print(f"Nærmeste Feature: {nearest_feature}")
        # Print resultatene
        # print(f"Nærmeste punkt: {nearest_feature.geometry}")
        # print(f"Attributter: {nearest_feature.attributes}")
        
        return nearest_feature.attributes
    else:
        print("Ingen gyldige funksjoner funnet innenfor det spesifiserte området.")
        return None


def update_sharepoint_trafostasjon(item_id, trafostasjon):
    #site_url = 'https://linjano.sharepoint.com/sites/yoursite'  # Bytt ut med ditt SharePoint Site URL
    site_id = siteid  # Bytt ut med ditt Site ID (du kan finne dette via Graph API)
    list_id = listid  # Bytt ut med ID eller navnet på SharePoint-listen

    # Headers for å autorisere forespørselen
    headers = {
        'Authorization': f'Bearer {token}'
    }
    # Eksempel på nye Trafostasjon verdi
    updated_fields = {
        #'Trafostasjonarcgis': trafostasjon
        'Trafostasjon': trafostasjon
    }

    print(f"Oppdaterer element med ID {item_id}...")

    # URL for å oppdatere feltene i dette elementet
    update_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items/{item_id}/fields'

    update_response = requests.patch(update_url, headers=headers, json=updated_fields)
    if update_response.status_code == 200:
        print(f"Element med ID {item_id} ble oppdatert med Nettstasjon.")
        return "ok"
    else:
        print(f"Feil ved oppdatering av element med ID {item_id}: {update_response.text}")
        return "error"


# Funksjon for å finne nærmeste punkt
def find_nearest_point(df, my_lat, my_lon):
    print(f"Min posisjon: {my_lat}, {my_lon}")
    #print(df)
    df['distance'] = df.apply(lambda row: haversine_distance(my_lat, my_lon, row['latitude'], row['longitude']), axis=1)
    if df.empty:
        return None
    nearest_point = df.loc[df['distance'].idxmin()]
    return nearest_point

trafostasjon_valg = get_sharepoint_trafos()
#feature_layer = get_arcgis_lag()

csv_file = "nettstasjoner_frakart.csv"

# Les data fra CSV-filen
df = pd.read_csv(csv_file, delimiter=';')

print(trafostasjon_valg)
data = get_sharepoint_list () # Kjør funksjonen for å hente data fra SharePoint-listen

#print(data)  # Skriv ut dataene for å se hva som er hentet

count = 0;

for item in data:

    count += 1

    print(f"Element {count}:")
    #if count > 10: 
    #    break

    fields = item['fields']  # Få tilgang til feltene i hvert listeelement

    lon = fields.get('Lon', '')
    lat = fields.get('Lat', '')
    Prosjektnavn = fields.get('Prosjektnavn', '')
    Trafostasjon = fields.get('Trafostasjon', '')
    itemid = item['id']

    try:
        lon = float(lon) if lon else None
        lat = float(lat) if lat else None
    except ValueError:
        lon = None
        lat = None    

    #if lon and lat:  # Sjekk om feltene er tomme
    if not Trafostasjon and lon and lat:  # Sjekk om feltene er tomme
        print(f"Prosjektnavn: {Prosjektnavn} {fields.get('Utbygger', '')}")
        #print(f"Trafostasjon: {Trafostasjon}")
        #print(f"Longitude: {lon}, Latitude: {lat}")
        #closest = find_closest( lon, lat)  # Kjør funksjonen for å finne nærmeste punkt
        closest = find_nearest_point(df, lat, lon)
        print(closest)
        print(f"Nærmeste punkt: {closest.get('navn', '')}")

        if closest is not None:

            """ distance = calculate_distance_inmeters(closest, {'x': lon, 'y': lat})
            print(f"Distanse: {distance} meter") """
            #driftsmerking = closest.get('DRIFTSMERKING', '')
            driftsmerking = closest.get('navn', '')
            #objectid = closest.get('OBJECTID', '')

            print(f"Driftsmerking: {driftsmerking}")
            #driftsmerking_cleaned = re.sub(r'[^a-zA-Z]', '', driftsmerking).lower().encode('utf-8').decode('unicode_escape')
            driftsmerking_cleaned = re.sub(r'[^\p{L}]', '', driftsmerking).lower()

            if driftsmerking_cleaned == "degnepollen":
                driftsmerking_cleaned = "deknepollen"

            
            print(f"Driftsmerking cleand: {driftsmerking_cleaned}")
            
            if driftsmerking_cleaned == "aheitrst":
                matched_value = "Åheim"
            elif  driftsmerking_cleaned == "bøistryn":
                matched_value = "Bø"
            elif driftsmerking_cleaned == "høyanger":
                matched_value = "Hydro Høyanger"
            else:
                # Søk etter en match i trafostasjon_valg ved å normalisere begge sidene for sammenligning

                print( "trafostasjonvalg", trafostasjon_valg )
                print( "driftsmerking_cleaned", driftsmerking_cleaned )
                matched_value = next((val for val in trafostasjon_valg if val.strip().lower() == driftsmerking_cleaned), None)
                

            if not matched_value:
                # Søk etter en match i trafostasjon_valg ved å normalisere begge sidene for sammenligning
                plassering = closest.get('Plassering', '')
                print(f"Plassering: {plassering}")
                #driftsmerking_cleaned = re.sub(r'[^a-zA-Z]', '', driftsmerking).lower().encode('utf-8').decode('unicode_escape')
                plassering_cleaned = re.sub(r'[^\p{L}]', '', plassering).lower()

                print(f"Plassering cleand før fiks: {plassering_cleaned}")

                if driftsmerking_cleaned == "degnepollen":
                    driftsmerking_cleaned = "deknepollen"
                
                matched_value = next((val for val in trafostasjon_valg if plassering_cleaned in val.strip().lower()), None)

            if matched_value:
                print(f"Match funnet for DRIFTSMERKING: {driftsmerking}")
                print(f"Verdi som matchet: {matched_value}")
                update_sharepoint_trafostasjon(itemid, matched_value)
            else:
                print(f"Ingen match for DRIFTSMERKING: {driftsmerking}")
                update_sharepoint_trafostasjon(itemid, driftsmerking)
            
            
            print("-----------------------------")
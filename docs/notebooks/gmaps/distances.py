import googlemaps

# Load googlemaps by using the API key
# API keys are generated in the 'Credentials' page, refer to following:
# https://developers.google.com/maps/documentation/geocoding/get-api-key
gmaps = googlemaps.Client(key="Add Your Key here")

# Find the distance between two points ("lat0, lon0", "lat1, lon1")
distances = gmaps.distance_matrix("-23.434453, -46.387014", "-23.429687, -46.416829")

print(distances)

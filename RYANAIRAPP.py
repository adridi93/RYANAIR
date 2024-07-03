import streamlit as st
from datetime import datetime, timedelta
from ryanair import Ryanair
from typing import List, Tuple, Dict

# Función para encontrar los vuelos más baratos hacia varios países
def find_cheapest_flights(origin, destination_countries, start_date, end_date, min_days, max_days, api) -> Dict[str, List[Tuple]]:
    all_trips = {country: [] for country in destination_countries}

    for outbound_date in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)):
        for num_days in range(min_days, max_days + 1):
            inbound_date = outbound_date + timedelta(days=num_days)
            if inbound_date > end_date:
                break

            trips = api.get_cheapest_return_flights(origin, outbound_date, outbound_date, inbound_date, inbound_date)
            if trips:
                for trip in trips:
                    for country in destination_countries:
                        if country.lower() in trip.outbound.destinationFull.lower():
                            all_trips[country].append((trip, num_days))
                            break

    # Ordenar los viajes de cada país por precio y mantener solo las 10 opciones más baratas
    for country in destination_countries:
        all_trips[country] = sorted(all_trips[country], key=lambda x: x[0].totalPrice)[:10]

    return all_trips

# Función para buscar los vuelos más baratos entre dos aeropuertos
def find_cheapest_flights_between_airports(origin, destination, start_date, end_date, min_days, max_days, api) -> List[Tuple]:
    all_trips = []

    for outbound_date in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)):
        for num_days in range(min_days, max_days + 1):
            inbound_date = outbound_date + timedelta(days=num_days)
            if inbound_date > end_date:
                break

            trips = api.get_cheapest_return_flights(origin, outbound_date, outbound_date, inbound_date, inbound_date)
            if trips:
                all_trips.extend((trip, num_days) for trip in trips if trip.outbound.destination == destination)

    return sorted(all_trips, key=lambda x: x[0].totalPrice)[:10]

# Función principal que define la interfaz de usuario
def main():
    st.title("Buscador de Vuelos Baratos")

    st.sidebar.title("Navegación")
    app_mode = st.sidebar.radio("Elige una opción", ["Buscar Vuelos Baratos", "Buscar Vuelos a Varios Países"])

    api = Ryanair(currency="EUR")

    if app_mode == "Buscar Vuelos Baratos":
        st.header("Buscar Vuelos Baratos Entre Dos Aeropuertos")

        origin = st.text_input("Código del aeropuerto de origen (por ejemplo, MAD para Madrid):").upper()
        destination = st.text_input("Código del aeropuerto de destino:").upper()
        start_date_str = st.date_input("Fecha de inicio de búsqueda:", value=datetime.today())
        end_date_str = st.date_input("Fecha de fin de búsqueda:", value=datetime.today() + timedelta(days=30))
        min_days = st.number_input("Número mínimo de días de estancia:", min_value=1, value=1)
        max_days = st.number_input("Número máximo de días de estancia:", min_value=1, value=14)

        if st.button("Buscar vuelos"):
            start_date = start_date_str
            end_date = end_date_str

            try:
                cheapest_trips = find_cheapest_flights_between_airports(origin, destination, start_date, end_date, min_days, max_days, api)

                if cheapest_trips:
                    st.write(f"Las 10 opciones más baratas encontradas (estancia de {min_days} a {max_days} días):")
                    for i, (trip, num_days) in enumerate(cheapest_trips, 1):
                        st.write(f"\nOpción {i}:")
                        st.write(f"Origen: {trip.outbound.originFull} ({trip.outbound.origin})")
                        st.write(f"Destino: {trip.outbound.destinationFull} ({trip.outbound.destination})")
                        st.write(f"Ida: {trip.outbound.departureTime}, Vuelo: {trip.outbound.flightNumber}, Precio: {trip.outbound.price} {trip.outbound.currency}")
                        st.write(f"Vuelta: {trip.inbound.departureTime}, Vuelo: {trip.inbound.flightNumber}, Precio: {trip.inbound.price} {trip.inbound.currency}")
                        st.write(f"Precio total: {trip.totalPrice} {trip.outbound.currency}")
                        st.write(f"Duración de la estancia: {num_days} días")
                else:
                    st.write("No se encontraron vuelos para las fechas y condiciones especificadas.")
            except Exception as e:
                st.error(f"Se produjo un error al buscar vuelos: {e}")

    elif app_mode == "Buscar Vuelos a Varios Países":
        st.header("Buscar Vuelos a Varios Países Desde Un Aeropuerto")

        origin = st.text_input("Código del aeropuerto de origen (por ejemplo, MAD para Madrid):").upper()
        destination_countries = [
            st.text_input("Introduzca el país de destino #1 (por ejemplo, Francia):"),
            st.text_input("Introduzca el país de destino #2 (por ejemplo, Italia):"),
            st.text_input("Introduzca el país de destino #3 (por ejemplo, Alemania):")
        ]
        start_date_str = st.date_input("Fecha de inicio de búsqueda:", value=datetime.today())
        end_date_str = st.date_input("Fecha de fin de búsqueda:", value=datetime.today() + timedelta(days=30))
        min_days = st.number_input("Número mínimo de días de estancia:", min_value=1, value=1)
        max_days = st.number_input("Número máximo de días de estancia:", min_value=1, value=14)

        if st.button("Buscar vuelos"):
            start_date = start_date_str
            end_date = end_date_str
            destination_countries = [country for country in destination_countries if country]

            try:
                cheapest_trips_by_country = find_cheapest_flights(origin, destination_countries, start_date, end_date, min_days, max_days, api)

                for country, trips in cheapest_trips_by_country.items():
                    st.write(f"\nLas 10 opciones más baratas encontradas para {country} (estancia de {min_days} a {max_days} días):")
                    if trips:
                        for i, (trip, num_days) in enumerate(trips, 1):
                            st.write(f"\nOpción {i}:")
                            st.write(f"Origen: {trip.outbound.originFull} ({trip.outbound.origin})")
                            st.write(f"Destino: {trip.outbound.destinationFull} ({trip.outbound.destination})")
                            st.write(f"Ida: {trip.outbound.departureTime}, Vuelo: {trip.outbound.flightNumber}, Precio: {trip.outbound.price} {trip.outbound.currency}")
                            st.write(f"Vuelta: {trip.inbound.departureTime}, Vuelo: {trip.inbound.flightNumber}, Precio: {trip.inbound.price} {trip.inbound.currency}")
                            st.write(f"Precio total: {trip.totalPrice} {trip.outbound.currency}")
                            st.write(f"Duración de la estancia: {num_days} días")
                    else:
                        st.write("No se encontraron vuelos para las fechas y condiciones especificadas.")
            except Exception as e:
                st.error(f"Se produjo un error al buscar vuelos: {e}")

if __name__ == "__main__":
    main()

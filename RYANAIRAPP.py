import streamlit as st
from datetime import datetime, timedelta
from ryanair import Ryanair
from typing import List, Tuple

def find_cheapest_flights(origin, destination, start_date, end_date, min_days, max_days, api) -> List[Tuple]:
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

def main():
    st.title("Buscador de Vuelos Baratos")

    api = Ryanair(currency="EUR")

    origin = st.text_input("Introduzca el código del aeropuerto de origen (por ejemplo, MAD para Madrid):").upper()
    destination = st.text_input("Introduzca el código del aeropuerto de destino:").upper()
    start_date_str = st.date_input("Introduzca la fecha de inicio de búsqueda:", value=datetime.today())
    end_date_str = st.date_input("Introduzca la fecha de fin de búsqueda:", value=datetime.today() + timedelta(days=30))
    min_days = st.number_input("Introduzca el número mínimo de días de estancia:", min_value=1, value=1)
    max_days = st.number_input("Introduzca el número máximo de días de estancia:", min_value=1, value=14)

    if st.button("Buscar vuelos"):
        start_date = start_date_str
        end_date = end_date_str

        cheapest_trips = find_cheapest_flights(origin, destination, start_date, end_date, min_days, max_days, api)

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

if __name__ == "__main__":
    main()

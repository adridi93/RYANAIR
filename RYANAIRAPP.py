import streamlit as st
from datetime import datetime, timedelta
from ryanair import Ryanair
from typing import List, Tuple
import yaml


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

st.set_page_config(page_title="Buscador de Vuelos Baratos de Ryanair", layout="wide")

st.title("Buscador de Vuelos Baratos de Ryanair")

# Inputs
col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("Código del aeropuerto de origen (por ejemplo, MAD para Madrid)").upper()
    destination = st.text_input("Código del aeropuerto de destino").upper()

with col2:
    start_date = st.date_input("Fecha de inicio de búsqueda", min_value=datetime.today())
    end_date = st.date_input("Fecha de fin de búsqueda", min_value=start_date)

col3, col4 = st.columns(2)

with col3:
    min_days = st.number_input("Número mínimo de días de estancia", min_value=1, value=1)

with col4:
    max_days = st.number_input("Número máximo de días de estancia", min_value=min_days, value=min_days)

if st.button("Buscar vuelos"):
    api = Ryanair(currency="EUR")
    
    cheapest_trips = find_cheapest_flights(origin, destination, start_date, end_date, min_days, max_days, api)

    if cheapest_trips:
        st.success(f"Las 10 opciones más baratas encontradas (estancia de {min_days} a {max_days} días):")
        for i, (trip, num_days) in enumerate(cheapest_trips, 1):
            with st.expander(f"Opción {i}: {trip.totalPrice} {trip.outbound.currency}"):
                st.write(f"Origen: {trip.outbound.originFull} ({trip.outbound.origin})")
                st.write(f"Destino: {trip.outbound.destinationFull} ({trip.outbound.destination})")
                st.write(f"Ida: {trip.outbound.departureTime}, Vuelo: {trip.outbound.flightNumber}, Precio: {trip.outbound.price} {trip.outbound.currency}")
                st.write(f"Vuelta: {trip.inbound.departureTime}, Vuelo: {trip.inbound.flightNumber}, Precio: {trip.inbound.price} {trip.inbound.currency}")
                st.write(f"Precio total: {trip.totalPrice} {trip.outbound.currency}")
                st.write(f"Duración de la estancia: {num_days} días")
    else:
        st.error("No se encontraron vuelos para las fechas y condiciones especificadas.")

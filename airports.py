"""
Common airports data for the airline demand analysis application.
"""

COMMON_AIRPORTS = [
    {
        "code": "ATL",
        "name": "Hartsfield-Jackson Atlanta International Airport",
        "city": "Atlanta",
        "country": "USA",
    },
    {
        "code": "PEK",
        "name": "Beijing Capital International Airport",
        "city": "Beijing",
        "country": "China",
    },
    {
        "code": "LHR",
        "name": "London Heathrow Airport",
        "city": "London",
        "country": "UK",
    },
    {
        "code": "HND",
        "name": "Tokyo Haneda Airport",
        "city": "Tokyo",
        "country": "Japan",
    },
    {
        "code": "ORD",
        "name": "O'Hare International Airport",
        "city": "Chicago",
        "country": "USA",
    },
    {
        "code": "LAX",
        "name": "Los Angeles International Airport",
        "city": "Los Angeles",
        "country": "USA",
    },
    {
        "code": "CDG",
        "name": "Charles de Gaulle Airport",
        "city": "Paris",
        "country": "France",
    },
    {
        "code": "DFW",
        "name": "Dallas/Fort Worth International Airport",
        "city": "Dallas",
        "country": "USA",
    },
    {
        "code": "FRA",
        "name": "Frankfurt Airport",
        "city": "Frankfurt",
        "country": "Germany",
    },
    {
        "code": "IST",
        "name": "Istanbul Airport",
        "city": "Istanbul",
        "country": "Turkey",
    },
    {
        "code": "AMS",
        "name": "Amsterdam Airport Schiphol",
        "city": "Amsterdam",
        "country": "Netherlands",
    },
    {
        "code": "CAN",
        "name": "Guangzhou Baiyun International Airport",
        "city": "Guangzhou",
        "country": "China",
    },
    {
        "code": "HKG",
        "name": "Hong Kong International Airport",
        "city": "Hong Kong",
        "country": "China",
    },
    {
        "code": "ICN",
        "name": "Incheon International Airport",
        "city": "Seoul",
        "country": "South Korea",
    },
    {
        "code": "DXB",
        "name": "Dubai International Airport",
        "city": "Dubai",
        "country": "UAE",
    },
    {
        "code": "JFK",
        "name": "John F. Kennedy International Airport",
        "city": "New York",
        "country": "USA",
    },
    {
        "code": "SIN",
        "name": "Singapore Changi Airport",
        "city": "Singapore",
        "country": "Singapore",
    },
    {
        "code": "MAD",
        "name": "Adolfo Suárez Madrid–Barajas Airport",
        "city": "Madrid",
        "country": "Spain",
    },
    {"code": "SYD", "name": "Sydney Airport", "city": "Sydney", "country": "Australia"},
    {
        "code": "YYZ",
        "name": "Toronto Pearson International Airport",
        "city": "Toronto",
        "country": "Canada",
    },
]


def get_airport_by_code(code):
    """
    Get airport details by IATA code.

    Args:
        code (str): The IATA airport code (e.g., 'JFK', 'LHR')

    Returns:
        dict: Airport details dictionary or None if not found
    """
    for airport in COMMON_AIRPORTS:
        if airport["code"] == code.upper():
            return airport
    return None


def search_airports(query):
    """
    Search airports by name, city, country or code.

    Args:
        query (str): Search query string

    Returns:
        list: List of matching airport dictionaries
    """
    query = query.lower()
    results = []

    for airport in COMMON_AIRPORTS:
        if (
            query in airport["name"].lower()
            or query in airport["city"].lower()
            or query in airport["country"].lower()
            or query in airport["code"].lower()
        ):
            results.append(airport)

    return results

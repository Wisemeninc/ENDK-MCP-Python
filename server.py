"""
Energinet Data Service MCP Server

This MCP server provides tools to query the Danish Energinet Data Service API,
which offers energy-related datasets including electricity prices, production,
consumption, and grid data.

API Documentation: https://www.energidataservice.dk/
"""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("energinet-dataservice")

# Constants
API_BASE = "https://api.energidataservice.dk"
DEFAULT_TIMEOUT = 30.0


async def make_api_request(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Make a request to the Energinet Data Service API with proper error handling."""
    url = f"{API_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


def format_records(records: list[dict], max_records: int = 10) -> str:
    """Format records into a readable string."""
    if not records:
        return "No records found."
    
    formatted = []
    for i, record in enumerate(records[:max_records]):
        record_str = f"Record {i + 1}:\n"
        for key, value in record.items():
            record_str += f"  {key}: {value}\n"
        formatted.append(record_str)
    
    result = "\n".join(formatted)
    if len(records) > max_records:
        result += f"\n... and {len(records) - max_records} more records"
    
    return result


@mcp.tool()
async def list_datasets() -> str:
    """
    List all available datasets from Energinet Data Service.
    
    Returns a list of dataset names that can be queried using the query_dataset tool.
    Common datasets include:
    - Elspotprices: Day-ahead electricity spot prices
    - ProductionConsumptionSettlement: Production and consumption data
    - ElectricitySuppliersPerGridarea: Electricity suppliers per grid area
    - CO2Emis: CO2 emissions from electricity and heating
    """
    data = await make_api_request("meta/dataset")
    
    if data is None:
        return "Unable to fetch dataset list from Energinet Data Service."
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    datasets = data.get("result", [])
    if not datasets:
        return "No datasets found."
    
    # Format dataset list
    dataset_names = []
    for ds in datasets:
        name = ds.get("name", "Unknown")
        description = ds.get("description", "No description")
        dataset_names.append(f"- {name}: {description}")
    
    return f"Available datasets ({len(datasets)} total):\n\n" + "\n".join(dataset_names)


@mcp.tool()
async def get_dataset_metadata(dataset_name: str) -> str:
    """
    Get metadata for a specific dataset including column names, types, and descriptions.
    
    Args:
        dataset_name: The name of the dataset (e.g., 'Elspotprices', 'CO2Emis')
    """
    data = await make_api_request(f"meta/{dataset_name}")
    
    if data is None:
        return f"Unable to fetch metadata for dataset '{dataset_name}'."
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    result = data.get("result", {})
    if not result:
        return f"No metadata found for dataset '{dataset_name}'."
    
    # Format metadata
    output = [f"Dataset: {dataset_name}"]
    
    if "description" in result:
        output.append(f"Description: {result['description']}")
    
    if "recordCount" in result:
        output.append(f"Total Records: {result['recordCount']}")
    
    columns = result.get("columns", [])
    if columns:
        output.append("\nColumns:")
        for col in columns:
            col_name = col.get("name", "Unknown")
            col_type = col.get("type", "Unknown")
            col_desc = col.get("description", "No description")
            output.append(f"  - {col_name} ({col_type}): {col_desc}")
    
    return "\n".join(output)


@mcp.tool()
async def query_dataset(
    dataset_name: str,
    limit: int = 10,
    offset: int = 0,
    start: str | None = None,
    end: str | None = None,
    filter: str | None = None,
    columns: str | None = None,
    sort: str | None = None
) -> str:
    """
    Query a dataset from Energinet Data Service.
    
    Args:
        dataset_name: The name of the dataset to query (e.g., 'Elspotprices', 'CO2Emis')
        limit: Maximum number of records to return (default: 10, max: 100)
        offset: Number of records to skip for pagination (default: 0)
        start: Start datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
        end: End datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
        filter: OData-style filter expression (e.g., '"PriceArea" = "DK1"')
        columns: Comma-separated list of columns to include
        sort: Column to sort by with direction (e.g., 'HourUTC DESC')
    
    Example queries:
    - Get latest electricity spot prices: dataset_name='Elspotprices', limit=5, sort='HourUTC DESC'
    - Get prices for DK1 area: dataset_name='Elspotprices', filter='"PriceArea" = "DK1"'
    """
    # Build query parameters
    params: dict[str, Any] = {
        "limit": min(limit, 100)  # Cap at 100 for reasonable response sizes
    }
    
    if offset > 0:
        params["offset"] = offset
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    if filter:
        params["filter"] = filter
    if columns:
        params["columns"] = columns
    if sort:
        params["sort"] = sort
    
    data = await make_api_request(f"dataset/{dataset_name}", params)
    
    if data is None:
        return f"Unable to query dataset '{dataset_name}'."
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    # Format response
    total = data.get("total", 0)
    records = data.get("records", [])
    
    output = [f"Dataset: {dataset_name}"]
    output.append(f"Total matching records: {total}")
    output.append(f"Records returned: {len(records)}")
    output.append("")
    output.append(format_records(records, max_records=limit))
    
    return "\n".join(output)


@mcp.tool()
async def get_electricity_prices(
    price_area: str = "DK1",
    limit: int = 24,
    start: str | None = None,
    end: str | None = None
) -> str:
    """
    Get electricity spot prices for a specific price area in Denmark.
    
    Args:
        price_area: The price area to query (DK1 for Western Denmark, DK2 for Eastern Denmark)
        limit: Maximum number of hourly records to return (default: 24 for one day)
        start: Start datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
        end: End datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
    
    Returns hourly spot prices in EUR/MWh and DKK/MWh.
    """
    params: dict[str, Any] = {
        "limit": min(limit, 100),
        "filter": f'"PriceArea" = "{price_area}"',
        "sort": "HourUTC DESC",
        "columns": "HourUTC,HourDK,PriceArea,SpotPriceDKK,SpotPriceEUR"
    }
    
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    data = await make_api_request("dataset/Elspotprices", params)
    
    if data is None:
        return f"Unable to fetch electricity prices for {price_area}."
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    records = data.get("records", [])
    
    if not records:
        return f"No electricity prices found for {price_area}."
    
    output = [f"Electricity Spot Prices for {price_area}"]
    output.append(f"(Prices in DKK/MWh and EUR/MWh)\n")
    
    for record in records:
        hour_dk = record.get("HourDK", record.get("HourUTC", "Unknown"))
        price_dkk = record.get("SpotPriceDKK", "N/A")
        price_eur = record.get("SpotPriceEUR", "N/A")
        
        # Format prices
        if isinstance(price_dkk, (int, float)):
            price_dkk = f"{price_dkk:.2f}"
        if isinstance(price_eur, (int, float)):
            price_eur = f"{price_eur:.2f}"
        
        output.append(f"{hour_dk}: {price_dkk} DKK/MWh ({price_eur} EUR/MWh)")
    
    return "\n".join(output)


@mcp.tool()
async def get_co2_emissions(
    limit: int = 24,
    start: str | None = None,
    end: str | None = None
) -> str:
    """
    Get CO2 emission data for electricity and district heating production in Denmark.
    
    Args:
        limit: Maximum number of records to return (default: 24)
        start: Start datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
        end: End datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
    
    Returns CO2 emission intensity in g/kWh for different price areas.
    """
    params: dict[str, Any] = {
        "limit": min(limit, 100),
        "sort": "Minutes5UTC DESC"
    }
    
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    data = await make_api_request("dataset/CO2Emis", params)
    
    if data is None:
        return "Unable to fetch CO2 emission data."
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    records = data.get("records", [])
    
    if not records:
        return "No CO2 emission data found."
    
    output = ["CO2 Emission Intensity (g CO2/kWh)\n"]
    
    for record in records:
        time = record.get("Minutes5DK", record.get("Minutes5UTC", "Unknown"))
        area = record.get("PriceArea", "Unknown")
        co2 = record.get("CO2Emission", "N/A")
        
        if isinstance(co2, (int, float)):
            co2 = f"{co2:.1f}"
        
        output.append(f"{time} ({area}): {co2} g/kWh")
    
    return "\n".join(output)


@mcp.tool()
async def get_production_consumption(
    price_area: str | None = None,
    limit: int = 24,
    start: str | None = None,
    end: str | None = None
) -> str:
    """
    Get electricity production and consumption settlement data for Denmark.
    
    Args:
        price_area: Optional price area filter (DK1 or DK2)
        limit: Maximum number of records to return (default: 24)
        start: Start datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
        end: End datetime for filtering (ISO format: YYYY-MM-DDTHH:MM)
    
    Returns production (wind, solar, thermal) and consumption data in MWh.
    """
    params: dict[str, Any] = {
        "limit": min(limit, 100),
        "sort": "HourUTC DESC"
    }
    
    if price_area:
        params["filter"] = f'"PriceArea" = "{price_area}"'
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    data = await make_api_request("dataset/ProductionConsumptionSettlement", params)
    
    if data is None:
        return "Unable to fetch production/consumption data."
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    records = data.get("records", [])
    
    if not records:
        return "No production/consumption data found."
    
    output = ["Electricity Production and Consumption (MWh)\n"]
    
    for record in records:
        hour = record.get("HourDK", record.get("HourUTC", "Unknown"))
        area = record.get("PriceArea", "Unknown")
        
        # Production sources
        onshore_wind = record.get("OnshoreWindPower", 0) or 0
        offshore_wind = record.get("OffshoreWindPower", 0) or 0
        solar = record.get("SolarPower", 0) or 0
        
        total_wind = onshore_wind + offshore_wind
        gross_consumption = record.get("GrossConsumption", "N/A")
        
        output.append(f"{hour} ({area}):")
        output.append(f"  Wind: {total_wind:.1f} MWh (Onshore: {onshore_wind:.1f}, Offshore: {offshore_wind:.1f})")
        output.append(f"  Solar: {solar:.1f} MWh")
        output.append(f"  Gross Consumption: {gross_consumption}")
        output.append("")
    
    return "\n".join(output)


def main():
    """Initialize and run the MCP server."""
    import sys
    import os
    
    # Check for --http flag to run in Streamable HTTP mode (recommended for network)
    # or --sse for legacy SSE mode
    if "--http" in sys.argv or "--sse" in sys.argv:
        # Get host and port from args or use defaults
        host = "0.0.0.0"  # Listen on all interfaces
        port = 9000
        
        for i, arg in enumerate(sys.argv):
            if arg == "--host" and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
            elif arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        
        # Determine transport type
        transport = "streamable-http" if "--http" in sys.argv else "sse"
        
        # Set environment variables for uvicorn (used by FastMCP)
        os.environ["UVICORN_HOST"] = host
        os.environ["UVICORN_PORT"] = str(port)
        
        print(f"Starting MCP server with {transport} transport on http://{host}:{port}")
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport=transport)
    else:
        # Default to stdio for local use
        mcp.run(transport='stdio')


if __name__ == "__main__":
    main()

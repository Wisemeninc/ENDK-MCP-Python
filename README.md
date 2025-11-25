# Energinet Data Service MCP Server

A Model Context Protocol (MCP) server that provides access to the Danish Energinet Data Service API. This API offers energy-related datasets including electricity prices, production, consumption, CO2 emissions, and grid data for Denmark.

## Features

This MCP server provides the following tools:

- **list_datasets**: List all available datasets from Energinet Data Service
- **get_dataset_metadata**: Get metadata for a specific dataset including column names and types
- **query_dataset**: Query any dataset with filtering, sorting, and pagination
- **get_electricity_prices**: Get electricity spot prices for DK1 (Western Denmark) or DK2 (Eastern Denmark)
- **get_co2_emissions**: Get CO2 emission intensity data for electricity production
- **get_production_consumption**: Get electricity production and consumption data including wind and solar

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

1. Clone or navigate to this repository:
```bash
cd EnerginetDataService
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Running the Server

### Using uv (recommended)
```bash
uv run server.py
```

### Using Python directly
```bash
python server.py
```

## Configuration with VS Code

This MCP server is pre-configured for use with VS Code's GitHub Copilot. The configuration is in `.vscode/mcp.json`.

To use the server:
1. Open this workspace in VS Code
2. Ensure the Python extension is installed
3. The MCP server will be available in GitHub Copilot's Agent Mode

## Example Queries

Once connected, you can ask questions like:

- "What datasets are available from Energinet?"
- "Get the latest electricity prices for Western Denmark (DK1)"
- "Show me the CO2 emissions for the last 24 hours"
- "What was the wind power production yesterday?"

## API Reference

The server connects to the Energinet Data Service API:
- Data Query: `https://api.energidataservice.dk/dataset`
- Metadata Query: `https://api.energidataservice.dk/meta`

For more information about the API, visit: https://www.energidataservice.dk/

## Common Datasets

| Dataset Name | Description |
|--------------|-------------|
| Elspotprices | Day-ahead electricity spot prices |
| CO2Emis | CO2 emissions from electricity production |
| ProductionConsumptionSettlement | Production and consumption by energy source |
| ElectricitySuppliersPerGridarea | Electricity suppliers per grid area |
| Capacity | Power plant capacity data |

## License

MIT License

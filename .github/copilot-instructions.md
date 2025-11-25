# Energinet Data Service MCP Server

This workspace contains an MCP (Model Context Protocol) server for accessing the Danish Energinet Data Service API.

## Project Overview

The MCP server provides tools to query Danish energy data including:
- Electricity spot prices (Elspotprices)
- CO2 emission intensity (CO2Emis)
- Production and consumption data (ProductionConsumptionSettlement)
- Dataset metadata and discovery

## Key Files

- `server.py` - Main MCP server implementation using FastMCP
- `pyproject.toml` - Project configuration and dependencies
- `.vscode/mcp.json` - VS Code MCP server configuration

## Development

### Running the Server
```bash
uv run server.py
```

### Testing with MCP Inspector
```bash
npx @modelcontextprotocol/inspector uv run server.py
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_datasets` | List all available datasets |
| `get_dataset_metadata` | Get column info for a dataset |
| `query_dataset` | Query any dataset with filters |
| `get_electricity_prices` | Get spot prices for DK1/DK2 |
| `get_co2_emissions` | Get CO2 emission data |
| `get_production_consumption` | Get wind/solar production data |

## API Documentation

- Energinet Data Service: https://www.energidataservice.dk/
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk

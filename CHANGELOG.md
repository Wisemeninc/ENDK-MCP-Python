# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-25

### Added
- Initial release of Energinet Data Service MCP Server
- **Tools:**
  - `list_datasets` - List all available datasets from Energinet Data Service
  - `get_dataset_metadata` - Get metadata for a specific dataset
  - `query_dataset` - Query any dataset with filtering, sorting, and pagination
  - `get_electricity_prices` - Get electricity spot prices for DK1/DK2
  - `get_co2_emissions` - Get CO2 emission intensity data
  - `get_production_consumption` - Get electricity production and consumption data
- **Transport options:**
  - STDIO transport for local use (default)
  - SSE transport for network access (`--sse` flag)
  - Streamable HTTP transport for modern MCP clients (`--http` flag)
- Docker support with Dockerfile and docker-compose.yml
- VS Code MCP configuration in `.vscode/mcp.json`
- Full API integration with https://api.energidataservice.dk/

### Technical Details
- Built with Python 3.10+ and FastMCP
- Uses httpx for async HTTP requests
- Default network port: 9000

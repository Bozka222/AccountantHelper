from fastmcp import FastMCP
from src.accountant_helper.mcp.tools.search import search_accounting_standards
from src.accountant_helper.mcp.tools.calculate import calculate_accounting_formula
from src.accountant_helper.mcp.tools.stats import count_standards
from src.accountant_helper.mcp.tools.citation import get_citation

mcp = FastMCP("AccountantHelper")

# Register tools
mcp.add_tool(search_accounting_standards)
mcp.add_tool(calculate_accounting_formula)
mcp.add_tool(count_standards)
mcp.add_tool(get_citation)

if __name__ == "__main__":
    mcp.run()

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import sys
import asyncio

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv", # Executable
    args=['run', 'python', 'mcp_server_tool.py'], # Optional command line arguments
    env=None # Optional environment variables
)

print("Starting the client...")

async def run():
    try:
        print("Connecting to the server...")
        async with stdio_client(server_params) as (read, write):
            print("Connected to the server.")
            # Remove the sampling_callback parameter as it's not supported
            async with ClientSession(read, write) as session:
                print("Client session started.")
                # Initialize the connection
                print("Initializing session...")
                try:
                    await asyncio.wait_for(session.initialize(), timeout=30.0)
                    print("Session initialized.")
                except asyncio.TimeoutError:
                    print("Session initialization timed out.")
                    return
                
                print("Listing tools...")
                tools = await session.list_tools()
                print("Available tools:", tools)
                
                # Call the add tool
                print("Calling add tool...")
                add_result = await session.call_tool("add", {'a':1,'b':2})
                print("Add result (1 + 2):", add_result)
                
    except Exception as e:
        print(f"An error occurred: {e}")

print("Running the client...")

if __name__ == "__main__":
    asyncio.run(run())
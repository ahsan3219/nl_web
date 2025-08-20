#!/usr/bin/env python3
"""
Debug script to test endpoint validation and path resolution
"""

import os
import sys
import asyncio

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def debug_endpoints():
    """Debug endpoint configuration and validation"""
    
    print("=== Endpoint Debug Test ===")
    
    try:
        from core.config import CONFIG
        from core.retriever import VectorDBClient
        
        print(f"✅ Config loaded successfully")
        print(f"✅ Current working directory: {os.getcwd()}")
        print(f"✅ NLWEB_OUTPUT_DIR: {os.getenv('NLWEB_OUTPUT_DIR')}")
        print(f"✅ Docker detected: {os.path.exists('/app')}")
        
        # Test 1: Check retrieval endpoints
        print(f"\n=== Retrieval Endpoints ===")
        for name, config in CONFIG.retrieval_endpoints.items():
            print(f"Endpoint: {name}")
            print(f"  Enabled: {config.enabled}")
            print(f"  DB Type: {config.db_type}")
            print(f"  Database Path: {config.database_path}")
            print(f"  API Endpoint: {config.api_endpoint}")
            print(f"  API Key: {'Set' if config.api_key else 'Not set'}")
            
            if config.database_path:
                resolved_path = CONFIG._resolve_path(config.database_path)
                print(f"  Resolved Path: {resolved_path}")
                print(f"  Path Exists: {os.path.exists(resolved_path)}")
        
        # Test 2: Check enabled endpoints
        print(f"\n=== Enabled Endpoints ===")
        enabled_endpoints = {name: config for name, config in CONFIG.retrieval_endpoints.items() if config.enabled}
        print(f"Total enabled endpoints: {len(enabled_endpoints)}")
        
        for name, config in enabled_endpoints.items():
            print(f"  {name}: {config.db_type}")
        
        # Test 3: Test VectorDBClient initialization
        print(f"\n=== VectorDBClient Test ===")
        try:
            client = VectorDBClient()
            print(f"✅ VectorDBClient created successfully")
            print(f"✅ Enabled endpoints: {list(client.enabled_endpoints.keys())}")
            
            # Test 4: Check if endpoints have valid credentials
            print(f"\n=== Credential Validation ===")
            for name, config in client.enabled_endpoints.items():
                has_creds = client._has_valid_credentials(name, config)
                print(f"  {name}: {has_creds}")
                
                if not has_creds:
                    print(f"    ❌ No valid credentials for {name}")
                    if config.db_type == "qdrant":
                        print(f"    Database path: {config.database_path}")
                        if config.database_path:
                            resolved_path = CONFIG._resolve_path(config.database_path)
                            print(f"    Resolved path: {resolved_path}")
                            print(f"    Path exists: {os.path.exists(resolved_path)}")
            
            # Test 5: Try to get a client
            print(f"\n=== Client Creation Test ===")
            if client.enabled_endpoints:
                first_endpoint = list(client.enabled_endpoints.keys())[0]
                print(f"Testing client creation for: {first_endpoint}")
                
                try:
                    db_client = await client.get_client(first_endpoint)
                    print(f"✅ Client created successfully for {first_endpoint}")
                except Exception as e:
                    print(f"❌ Failed to create client for {first_endpoint}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ No enabled endpoints found")
                
        except Exception as e:
            print(f"❌ Failed to create VectorDBClient: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_endpoints())
    sys.exit(0 if success else 1)



import os
import sys
import platform
import subprocess

def get_version(package):
    try:
        import importlib.metadata
        return importlib.metadata.version(package)
    except:
        try:
            # Fallback for older python
            import pkg_resources
            return pkg_resources.get_distribution(package).version
        except:
            return "Not Found"

def run_diagnostics():
    print("=== ENVIRONMENT DIAGNOSTICS ===")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Executable: {sys.executable}")
    
    print("\n=== PACKAGE VERSIONS ===")
    packages = ["groq", "langchain", "langchain-groq", "httpx", "pydantic", "langchain-core"]
    for p in packages:
        print(f"{p}: {get_version(p)}")
        
    print("\n=== PROXY ENV VARS ===")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
    for var in proxy_vars:
        val = os.environ.get(var)
        print(f"{var}: {'[REDACTED]' if val else 'Not Set'}")

    print("\n=== TESTING CHATGROQ INIT ===")
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(api_key="dry_run_test")
        print("ChatGroq dry-run init: SUCCESS")
    except Exception as e:
        print(f"ChatGroq dry-run init: FAILED")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        
    print("\n===============================")

if __name__ == "__main__":
    run_diagnostics()

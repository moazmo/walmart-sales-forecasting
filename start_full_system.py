"""
Full System Startup Script
==========================

This script starts the complete Walmart Sales Forecasting system including:
- Database initialization
- API server
- Frontend development server (optional)

Usage:
    python start_full_system.py [--frontend]
"""

import sys
import os
import subprocess
import time
import argparse
from pathlib import Path

# Try to import requests, install if not available
try:
    import requests
except ImportError:
    print("📦 Installing requests...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], check=True)
    import requests

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker to run the full system.")
        return False

def check_node():
    """Check if Node.js is available for frontend development."""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Node.js available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Node.js not found. Frontend development server won't be available.")
        return False

def start_database():
    """Start database services using Docker Compose."""
    print("🗄️  Starting database services...")
    
    try:
        # Start only database services
        subprocess.run([
            'docker-compose', 'up', '-d', 'postgres', 'redis'
        ], check=True, cwd=PROJECT_ROOT)
        
        print("✅ Database services started")
        
        # Wait for database to be ready
        print("⏳ Waiting for database to be ready...")
        time.sleep(10)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start database services: {e}")
        return False

def check_port_available(port):
    """Check if a port is available."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def check_api_server_running():
    """Check if API server is already running."""
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server."""
    print("🚀 Starting API server...")
    
    # Check if API server is already running
    if check_api_server_running():
        print("✅ API server is already running")
        print("📊 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        return "already_running"
    
    # Check if port is available
    if not check_port_available(8000):
        print("❌ Port 8000 is in use by another process")
        print("💡 Please stop the existing process or use a different port")
        return None
    
    try:
        # Initialize database tables
        from src.database import create_tables, test_connection
        
        if not test_connection():
            print("❌ Database connection failed")
            return False
            
        create_tables()
        print("✅ Database tables initialized")
        
        # Start API server in background
        api_process = subprocess.Popen([
            sys.executable, 'start_api.py'
        ], cwd=PROJECT_ROOT)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Verify the server started successfully
        if check_api_server_running():
            print("✅ API server started successfully (PID: {})".format(api_process.pid))
            return api_process
        else:
            print("❌ API server failed to start properly")
            api_process.terminate()
            return None
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_frontend():
    """Start the frontend development server."""
    print("🎨 Starting frontend development server...")
    
    frontend_dir = PROJECT_ROOT / 'frontend'
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # Install dependencies if needed
        if not (frontend_dir / 'node_modules').exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(['npm', 'install'], 
                         check=True, cwd=frontend_dir)
        
        # Start development server
        frontend_process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], cwd=frontend_dir)
        
        print("✅ Frontend server started (PID: {})".format(frontend_process.pid))
        return frontend_process
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None

def kill_process_on_port(port):
    """Kill process running on specified port (Windows)."""
    try:
        # Find process using the port
        result = subprocess.run([
            'netstat', '-ano'
        ], capture_output=True, text=True, check=True)
        
        lines = result.stdout.split('\n')
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], 
                                     capture_output=True, check=True)
                        print(f"✅ Killed process {pid} on port {port}")
                        return True
                    except subprocess.CalledProcessError:
                        pass
        return False
    except Exception:
        return False

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description='Start Walmart Sales Forecasting System')
    parser.add_argument('--frontend', action='store_true', 
                       help='Also start frontend development server')
    parser.add_argument('--docker-only', action='store_true',
                       help='Use Docker Compose for all services')
    parser.add_argument('--kill-existing', action='store_true',
                       help='Kill existing processes on required ports')
    
    args = parser.parse_args()
    
    print("🏪 Walmart Sales Forecasting - Full System Startup")
    print("=" * 60)
    
    # Check prerequisites
    if not check_docker():
        sys.exit(1)
    
    if args.frontend and not check_node():
        print("⚠️  Continuing without frontend development server")
        args.frontend = False
    
    processes = []
    
    try:
        if args.docker_only:
            # Use Docker Compose for everything
            print("🐳 Starting all services with Docker Compose...")
            subprocess.run(['docker-compose', 'up', '--build'], 
                         check=True, cwd=PROJECT_ROOT)
        else:
            # Start services individually
            
            # 1. Start database services
            if not start_database():
                sys.exit(1)
            
            # 2. Start API server
            if args.kill_existing:
                print("🔄 Checking for existing processes...")
                kill_process_on_port(8000)
                time.sleep(2)
            
            api_process = start_api_server()
            if api_process is None:
                print("💡 Try running with --kill-existing flag to stop existing processes")
                sys.exit(1)
            elif api_process != "already_running":
                processes.append(api_process)
            
            # 3. Start frontend (optional)
            if args.frontend:
                frontend_process = start_frontend()
                if frontend_process:
                    processes.append(frontend_process)
            
            print("\n" + "=" * 60)
            print("🎉 System startup completed!")
            print("=" * 60)
            print("📊 API Server: http://localhost:8000")
            print("📖 API Docs: http://localhost:8000/docs")
            print("🔍 Health Check: http://localhost:8000/health")
            
            if args.frontend:
                print("🎨 Frontend: http://localhost:3000")
            
            print("🗄️  Database: PostgreSQL on localhost:5432")
            print("🔄 Redis: localhost:6379")
            print("\n💡 Press Ctrl+C to stop all services")
            
            # Wait for processes
            try:
                for process in processes:
                    process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down services...")
                for process in processes:
                    process.terminate()
                
                # Stop Docker services
                subprocess.run(['docker-compose', 'down'], 
                             cwd=PROJECT_ROOT, capture_output=True)
                print("✅ All services stopped")
    
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
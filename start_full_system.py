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

def start_api_server():
    """Start the API server."""
    print("🚀 Starting API server...")
    
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
        
        print("✅ API server started (PID: {})".format(api_process.pid))
        return api_process
        
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

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description='Start Walmart Sales Forecasting System')
    parser.add_argument('--frontend', action='store_true', 
                       help='Also start frontend development server')
    parser.add_argument('--docker-only', action='store_true',
                       help='Use Docker Compose for all services')
    
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
            api_process = start_api_server()
            if not api_process:
                sys.exit(1)
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
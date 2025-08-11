#!/usr/bin/env python3
"""
Enhanced Fullstack Startup Script
Starts backend (Flask) and frontend (Vite/React) servers with improved error handling,
logging, health checks, and graceful shutdown.

Usage: 
  python3 start_fullstack.py [options]
  
Options:
  --backend-only    Start only the backend server
  --frontend-only   Start only the frontend server  
  --dev            Enable development mode with auto-reload
  --port-backend   Backend port (default: 3000)
  --port-frontend  Frontend port (default: 3001)
  --check-deps     Check dependencies before starting
"""
import os
import subprocess
import sys
import signal
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = SCRIPT_DIR.parent / "backend"
FRONTEND_DIR = SCRIPT_DIR.parent / "frontend"
DEFAULT_BACKEND_PORT = 3000
DEFAULT_FRONTEND_PORT = 3001

# Global process handles
backend_proc = None
frontend_proc = None
startup_time = None

def log(message, level="INFO"):
    """Enhanced logging with timestamps"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    icon = icons.get(level, "📝")
    print(f"[{timestamp}] {icon}  {message}")

def check_port_available(port, service_name):
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            log(f"Port {port} is already in use (needed for {service_name})", "ERROR")
            return False

def check_dependencies():
    """Check if required dependencies are installed"""
    log("Checking dependencies...")
    
    # Check Python dependencies
    try:
        os.chdir(BACKEND_DIR)
        result = subprocess.run(["pipenv", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            log("Pipenv not found. Install with: pip install pipenv", "ERROR")
            return False
        log("✓ Pipenv found", "SUCCESS")
        
        # Check if Pipfile exists and dependencies are installed
        if not (BACKEND_DIR / "Pipfile").exists():
            log("Pipfile not found in backend directory", "ERROR")
            return False
            
        log("Checking Python dependencies...", "INFO")
        result = subprocess.run(["pipenv", "check"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            log("Python dependencies check failed. Run: pipenv install", "WARNING")
        else:
            log("✓ Python dependencies OK", "SUCCESS")
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        log("Failed to check Python dependencies", "ERROR")
        return False
    
    # Check Node dependencies  
    try:
        os.chdir(FRONTEND_DIR)
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            log("Node.js not found. Please install Node.js", "ERROR")
            return False
        
        node_version = result.stdout.strip()
        log(f"✓ Node.js found: {node_version}", "SUCCESS")
        
        result = subprocess.run(["npm", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            log("npm not found", "ERROR")
            return False
            
        npm_version = result.stdout.strip()
        log(f"✓ npm found: {npm_version}", "SUCCESS")
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        log("Failed to check Node.js dependencies", "ERROR")
        return False
    
    os.chdir(SCRIPT_DIR)
    return True

def wait_for_backend_health(port, timeout=30):
    """Wait for backend to be healthy"""
    log(f"Waiting for backend health check on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                log("✓ Backend is healthy and ready", "SUCCESS")
                return True
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            pass
        
        time.sleep(1)
        if backend_proc and backend_proc.poll() is not None:
            log("Backend process died during startup", "ERROR")
            return False
    
    # Fallback: check root endpoint if /health doesn't exist
    try:
        response = requests.get(f"http://localhost:{port}/", timeout=2)
        if response.status_code == 200:
            log("✓ Backend is responding (no health endpoint)", "SUCCESS")
            return True
    except:
        pass
    
    log(f"Backend failed to start within {timeout} seconds", "ERROR")
    return False

def start_backend(port=DEFAULT_BACKEND_PORT, dev_mode=False):
    """Start the Flask backend server"""
    global backend_proc
    
    log("Starting Flask backend server...")
    
    # Verify backend directory and files
    if not BACKEND_DIR.exists():
        log(f"Backend directory not found: {BACKEND_DIR}", "ERROR")
        return False
        
    if not (BACKEND_DIR / "app.py").exists():
        log("app.py not found in backend directory", "ERROR")
        return False
    
    if not check_port_available(port, "backend"):
        return False
    
    # Change to backend directory
    os.chdir(BACKEND_DIR)
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env["FLASK_DEBUG"] = "1" if dev_mode else "0"
        env["PORT"] = str(port)
        
        # Start the backend process
        cmd = ["pipenv", "run", "python3", "app.py"]
        backend_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env
        )
        
        log(f"Backend started with PID {backend_proc.pid} on port {port}", "SUCCESS")
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if backend_proc.poll() is not None:
            log("Backend process exited immediately", "ERROR")
            return False
            
        return True
        
    except Exception as e:
        log(f"Failed to start backend: {e}", "ERROR")
        return False
    finally:
        os.chdir(SCRIPT_DIR)

def start_frontend(port=DEFAULT_FRONTEND_PORT):
    """Start the React frontend server"""
    global frontend_proc
    
    log("Starting React frontend server...")
    
    # Verify frontend directory
    if not FRONTEND_DIR.exists():
        log(f"Frontend directory not found: {FRONTEND_DIR}", "ERROR")
        return False
        
    if not (FRONTEND_DIR / "package.json").exists():
        log("package.json not found in frontend directory", "ERROR")
        return False
    
    if not check_port_available(port, "frontend"):
        return False
    
    # Change to frontend directory
    os.chdir(FRONTEND_DIR)
    
    try:
        # Install dependencies if node_modules doesn't exist
        if not (FRONTEND_DIR / "node_modules").exists():
            log("Installing frontend dependencies...")
            result = subprocess.run(["npm", "install"], check=True, timeout=120)
            log("✓ Frontend dependencies installed", "SUCCESS")
        
        # Set environment variables for frontend
        env = os.environ.copy()
        env["PORT"] = str(port)
        env["BROWSER"] = "none"  # Prevent automatic browser opening
        
        # Start the frontend process
        cmd = ["npm", "start"]
        frontend_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env
        )
        
        log(f"Frontend started with PID {frontend_proc.pid} on port {port}", "SUCCESS")
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if frontend_proc.poll() is not None:
            log("Frontend process exited immediately", "ERROR")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        log("Frontend dependency installation timed out", "ERROR")
        return False
    except Exception as e:
        log(f"Failed to start frontend: {e}", "ERROR")
        return False
    finally:
        os.chdir(SCRIPT_DIR)

def cleanup(signum=None, frame=None):
    """Gracefully shutdown both servers"""
    log("Shutting down servers...")
    
    if backend_proc and backend_proc.poll() is None:
        log("Stopping backend server...")
        backend_proc.terminate()
        try:
            backend_proc.wait(timeout=5)
            log("✓ Backend stopped", "SUCCESS")
        except subprocess.TimeoutExpired:
            log("Backend didn't stop gracefully, killing...", "WARNING")
            backend_proc.kill()
    
    if frontend_proc and frontend_proc.poll() is None:
        log("Stopping frontend server...")
        frontend_proc.terminate()
        try:
            frontend_proc.wait(timeout=5)
            log("✓ Frontend stopped", "SUCCESS")
        except subprocess.TimeoutExpired:
            log("Frontend didn't stop gracefully, killing...", "WARNING")
            frontend_proc.kill()
    
    if startup_time:
        runtime = datetime.now() - startup_time
        log(f"Total runtime: {runtime}", "INFO")
    
    log("Shutdown complete", "SUCCESS")
    sys.exit(0)

def monitor_processes(backend_port, frontend_port):
    """Monitor both processes and handle failures"""
    log("Monitoring processes... Press Ctrl+C to stop")
    log(f"🌐 Backend: http://localhost:{backend_port}")
    log(f"🖥️  Frontend: http://localhost:{frontend_port}")
    log(f"📚 API Docs: http://localhost:{backend_port}/swagger/")
    
    try:
        while True:
            # Check backend
            if backend_proc and backend_proc.poll() is not None:
                log("Backend process died unexpectedly", "ERROR")
                break
            
            # Check frontend
            if frontend_proc and frontend_proc.poll() is not None:
                log("Frontend process died unexpectedly", "ERROR")
                break
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        log("Received interrupt signal", "INFO")
    
    cleanup()

def main():
    """Main entry point with argument parsing"""
    global startup_time
    startup_time = datetime.now()
    
    parser = argparse.ArgumentParser(description="Start fullstack development environment")
    parser.add_argument("--backend-only", action="store_true", help="Start only backend")
    parser.add_argument("--frontend-only", action="store_true", help="Start only frontend")
    parser.add_argument("--dev", action="store_true", help="Enable development mode")
    parser.add_argument("--port-backend", type=int, default=DEFAULT_BACKEND_PORT, help="Backend port")
    parser.add_argument("--port-frontend", type=int, default=DEFAULT_FRONTEND_PORT, help="Frontend port")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies before starting")
    parser.add_argument("--no-health-check", action="store_true", help="Skip backend health check")
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    log("🚀 Starting Star Wars Fullstack Development Environment")
    log(f"📁 Backend: {BACKEND_DIR}")
    log(f"📁 Frontend: {FRONTEND_DIR}")
    
    # Check dependencies if requested
    if args.check_deps:
        if not check_dependencies():
            log("Dependency check failed", "ERROR")
            sys.exit(1)
    
    # Start backend
    if not args.frontend_only:
        if not start_backend(args.port_backend, args.dev):
            log("Failed to start backend", "ERROR")
            sys.exit(1)
        
        # Health check
        if not args.no_health_check:
            if not wait_for_backend_health(args.port_backend):
                log("Backend health check failed", "WARNING")
    
    # Start frontend
    if not args.backend_only:
        if not start_frontend(args.port_frontend):
            log("Failed to start frontend", "ERROR")
            cleanup()
            sys.exit(1)
    
    # Monitor processes
    monitor_processes(args.port_backend, args.port_frontend)

if __name__ == "__main__":
    main()
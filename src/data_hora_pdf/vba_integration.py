"""
VBA Integration Module for CarimboPDF
Provides REST API endpoints for Word VBA integration with DETRAN vehicle queries.
"""

import json
import logging
import os
from datetime import datetime, date
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, Response
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VehicleData:
    """Data contract for vehicle information"""
    placa: str
    uf: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano_fabricacao: Optional[int] = None
    ano_modelo: Optional[int] = None
    cor: Optional[str] = None
    combustivel: Optional[str] = None
    categoria: Optional[str] = None
    proprietario: Optional[str] = None
    municipio: Optional[str] = None
    situacao: Optional[str] = None
    consulta_timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class ApiResponse:
    """Standard API response format"""
    success: bool
    data: Optional[Any] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        if hasattr(self.data, 'to_dict'):
            result['data'] = self.data.to_dict()
        return result

class SGDWDetranService:
    """
    Simulates SGDW-ConsultaSC.Servico DLL functionality
    In production, this would interface with the actual .NET DLL
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "SGDW-ConsultaSC.ini"
        self.session_active = False
        self.last_login = None
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from INI file (simulated)"""
        default_config = {
            "detran_url": "https://detran.sc.gov.br",
            "headless_mode": True,
            "timeout_seconds": 30,
            "max_retries": 3,
            "regional_api": "SC"
        }
        
        # In production, load from actual INI file
        config_file = Path(self.config_path)
        if config_file.exists():
            # Parse INI file
            pass
            
        return default_config
    
    def login(self, username: str = None, password: str = None) -> bool:
        """
        Simulate login to DETRAN system
        In production, this would call the actual DLL login method
        """
        try:
            # Simulate login delay
            time.sleep(0.5)
            
            # For demo purposes, always succeed
            self.session_active = True
            self.last_login = datetime.now()
            logger.info(f"DETRAN login successful at {self.last_login}")
            return True
            
        except Exception as e:
            logger.error(f"DETRAN login failed: {e}")
            return False
    
    def consultar_veiculo(self, placa: str, uf: str = "SC") -> Optional[VehicleData]:
        """
        Query vehicle information from DETRAN
        In production, this would call the actual DLL query method
        """
        if not self.session_active:
            if not self.login():
                return None
        
        try:
            # Simulate query delay
            time.sleep(0.3)
            
            # For demo purposes, return mock data based on license plate
            mock_data = self._generate_mock_vehicle_data(placa, uf)
            return mock_data
            
        except Exception as e:
            logger.error(f"Vehicle query failed for {placa}: {e}")
            return None
    
    def _generate_mock_vehicle_data(self, placa: str, uf: str) -> VehicleData:
        """Generate realistic mock vehicle data for demonstration"""
        mock_vehicles = {
            "ABC1234": {
                "marca": "VOLKSWAGEN",
                "modelo": "GOL",
                "ano_fabricacao": 2020,
                "ano_modelo": 2020,
                "cor": "BRANCA",
                "combustivel": "FLEX",
                "categoria": "PARTICULAR",
                "municipio": "FLORIANÓPOLIS"
            },
            "XYZ5678": {
                "marca": "FIAT",
                "modelo": "UNO",
                "ano_fabricacao": 2018,
                "ano_modelo": 2019,
                "cor": "PRATA",
                "combustivel": "FLEX",
                "categoria": "PARTICULAR",
                "municipio": "JOINVILLE"
            }
        }
        
        # Get mock data or use default
        vehicle_info = mock_vehicles.get(placa.upper(), {
            "marca": "CHEVROLET",
            "modelo": "ONIX",
            "ano_fabricacao": 2021,
            "ano_modelo": 2021,
            "cor": "AZUL",
            "combustivel": "FLEX",
            "categoria": "PARTICULAR",
            "municipio": "BLUMENAU"
        })
        
        return VehicleData(
            placa=placa.upper(),
            uf=uf.upper(),
            situacao="REGULAR",
            proprietario="PROPRIETÁRIO EXEMPLO",
            consulta_timestamp=datetime.now().isoformat(),
            **vehicle_info
        )

class VBAIntegrationAPI:
    """REST API service for VBA integration"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = Flask(__name__)
        self.detran_service = SGDWDetranService()
        self._setup_routes()
        
    def _setup_routes(self):
        """Configure API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify(ApiResponse(
                success=True,
                data={"status": "healthy", "service": "CarimboPDF-VBA-Integration"}
            ).to_dict())
        
        @self.app.route('/consulta/placa', methods=['POST'])
        def consultar_placa():
            """Query vehicle by license plate"""
            try:
                data = request.get_json()
                if not data or 'placa' not in data:
                    return jsonify(ApiResponse(
                        success=False,
                        error_code="INVALID_REQUEST",
                        error_message="Campo 'placa' é obrigatório"
                    ).to_dict()), 400
                
                placa = data['placa'].strip().upper()
                uf = data.get('uf', 'SC').strip().upper()
                
                # Validate license plate format (basic)
                if len(placa) < 7:
                    return jsonify(ApiResponse(
                        success=False,
                        error_code="INVALID_PLATE",
                        error_message="Formato de placa inválido"
                    ).to_dict()), 400
                
                # Query vehicle data
                vehicle_data = self.detran_service.consultar_veiculo(placa, uf)
                
                if vehicle_data is None:
                    return jsonify(ApiResponse(
                        success=False,
                        error_code="VEHICLE_NOT_FOUND",
                        error_message="Veículo não encontrado ou erro no sistema DETRAN"
                    ).to_dict()), 404
                
                return jsonify(ApiResponse(
                    success=True,
                    data=vehicle_data
                ).to_dict())
                
            except Exception as e:
                logger.error(f"Error in consultar_placa: {e}")
                return jsonify(ApiResponse(
                    success=False,
                    error_code="INTERNAL_ERROR",
                    error_message="Erro interno do servidor"
                ).to_dict()), 500
        
        @self.app.route('/auth/login', methods=['POST'])
        def login():
            """Authenticate with DETRAN system"""
            try:
                data = request.get_json()
                username = data.get('username') if data else None
                password = data.get('password') if data else None
                
                success = self.detran_service.login(username, password)
                
                if success:
                    return jsonify(ApiResponse(
                        success=True,
                        data={"session_active": True, "login_time": self.detran_service.last_login.isoformat()}
                    ).to_dict())
                else:
                    return jsonify(ApiResponse(
                        success=False,
                        error_code="LOGIN_FAILED",
                        error_message="Falha na autenticação com DETRAN"
                    ).to_dict()), 401
                    
            except Exception as e:
                logger.error(f"Error in login: {e}")
                return jsonify(ApiResponse(
                    success=False,
                    error_code="INTERNAL_ERROR",
                    error_message="Erro interno do servidor"
                ).to_dict()), 500
        
        @self.app.route('/auth/status', methods=['GET'])
        def auth_status():
            """Check authentication status"""
            return jsonify(ApiResponse(
                success=True,
                data={
                    "session_active": self.detran_service.session_active,
                    "last_login": self.detran_service.last_login.isoformat() if self.detran_service.last_login else None
                }
            ).to_dict())
    
    def run(self, debug: bool = False):
        """Start the API service"""
        logger.info(f"Starting VBA Integration API on port {self.port}")
        self.app.run(host='127.0.0.1', port=self.port, debug=debug)

def start_api_service(port: int = 8080, debug: bool = False):
    """Start the API service in a separate thread"""
    api = VBAIntegrationAPI(port)
    
    def run_api():
        api.run(debug=debug)
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    return api_thread

if __name__ == "__main__":
    # CLI mode for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="VBA Integration API for CarimboPDF")
    parser.add_argument("--port", type=int, default=8080, help="API server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    api = VBAIntegrationAPI(args.port)
    api.run(debug=args.debug)
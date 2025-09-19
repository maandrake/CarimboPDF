#!/usr/bin/env python3
"""
CLI Tool for DETRAN Vehicle Query - CarimboPDF Integration
Provides command-line interface for querying vehicle information offline or as an alternative to the REST API.

Usage examples:
    python vehicle_query_cli.py --placa ABC1234 --uf SC
    python vehicle_query_cli.py --placa ABC1234 --output vehicle_data.json
    python vehicle_query_cli.py --placa ABC1234 --format text
"""

import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import from the VBA integration module
try:
    from .vba_integration import SGDWDetranService, VehicleData, ApiResponse
except ImportError:
    # Handle direct execution
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from vba_integration import SGDWDetranService, VehicleData, ApiResponse

class VehicleQueryCLI:
    """Command-line interface for vehicle queries"""
    
    def __init__(self, config_path: str = None):
        self.detran_service = SGDWDetranService(config_path)
        
    def query_vehicle(self, placa: str, uf: str = "SC") -> Optional[VehicleData]:
        """Query vehicle information"""
        try:
            # Ensure login
            if not self.detran_service.session_active:
                if not self.detran_service.login():
                    return None
            
            return self.detran_service.consultar_veiculo(placa, uf)
            
        except Exception as e:
            print(f"Erro ao consultar veículo: {e}", file=sys.stderr)
            return None
    
    def format_output(self, vehicle: VehicleData, format_type: str = "json") -> str:
        """Format vehicle data for output"""
        if format_type.lower() == "json":
            return json.dumps(vehicle.to_dict(), indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "text":
            return self._format_text_output(vehicle)
        
        elif format_type.lower() == "csv":
            return self._format_csv_output(vehicle)
        
        else:
            raise ValueError(f"Formato não suportado: {format_type}")
    
    def _format_text_output(self, vehicle: VehicleData) -> str:
        """Format vehicle data as human-readable text"""
        lines = [
            "═" * 50,
            "DADOS DO VEÍCULO",
            "═" * 50,
            f"Placa: {vehicle.placa}",
            f"UF: {vehicle.uf}",
            f"Marca: {vehicle.marca or 'N/A'}",
            f"Modelo: {vehicle.modelo or 'N/A'}",
            f"Ano de Fabricação: {vehicle.ano_fabricacao or 'N/A'}",
            f"Ano do Modelo: {vehicle.ano_modelo or 'N/A'}",
            f"Cor: {vehicle.cor or 'N/A'}",
            f"Combustível: {vehicle.combustivel or 'N/A'}",
            f"Categoria: {vehicle.categoria or 'N/A'}",
            f"Proprietário: {vehicle.proprietario or 'N/A'}",
            f"Município: {vehicle.municipio or 'N/A'}",
            f"Situação: {vehicle.situacao or 'N/A'}",
            f"Consulta realizada em: {vehicle.consulta_timestamp or 'N/A'}",
            "═" * 50
        ]
        return "\n".join(lines)
    
    def _format_csv_output(self, vehicle: VehicleData) -> str:
        """Format vehicle data as CSV"""
        header = "placa,uf,marca,modelo,ano_fabricacao,ano_modelo,cor,combustivel,categoria,proprietario,municipio,situacao,consulta_timestamp"
        data = f"{vehicle.placa},{vehicle.uf},{vehicle.marca or ''},{vehicle.modelo or ''},{vehicle.ano_fabricacao or ''},{vehicle.ano_modelo or ''},{vehicle.cor or ''},{vehicle.combustivel or ''},{vehicle.categoria or ''},{vehicle.proprietario or ''},{vehicle.municipio or ''},{vehicle.situacao or ''},{vehicle.consulta_timestamp or ''}"
        return f"{header}\n{data}"

def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="CLI para consulta de veículos - Integração CarimboPDF/DETRAN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  Consulta básica:
    python vehicle_query_cli.py --placa ABC1234 --uf SC

  Salvar em arquivo JSON:
    python vehicle_query_cli.py --placa ABC1234 --output dados_veiculo.json

  Formato texto legível:
    python vehicle_query_cli.py --placa ABC1234 --format text

  Múltiplas placas de arquivo:
    python vehicle_query_cli.py --batch placas.txt --output resultados.json

  Configuração personalizada:
    python vehicle_query_cli.py --placa ABC1234 --config custom_config.ini
        """
    )
    
    # Argumentos principais
    parser.add_argument(
        "--placa", 
        type=str, 
        help="Placa do veículo a ser consultado"
    )
    
    parser.add_argument(
        "--uf", 
        type=str, 
        default="SC",
        choices=["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
        help="Estado de origem do veículo (padrão: SC)"
    )
    
    # Opções de saída
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Arquivo de saída para salvar os dados (se omitido, imprime no stdout)"
    )
    
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["json", "text", "csv"],
        default="json",
        help="Formato de saída dos dados (padrão: json)"
    )
    
    # Processamento em lote
    parser.add_argument(
        "--batch", "-b",
        type=str,
        help="Arquivo com lista de placas para processamento em lote (uma por linha)"
    )
    
    # Configuração
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Caminho para arquivo de configuração personalizado"
    )
    
    # Opções de debug
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Exibir informações detalhadas durante a execução"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suprimir mensagens de status (apenas dados)"
    )
    
    # Teste de conectividade
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Testar conectividade com o sistema DETRAN"
    )
    
    return parser

def process_batch_file(batch_file: str, cli: VehicleQueryCLI, uf: str, verbose: bool) -> Dict[str, Any]:
    """Process multiple plates from a file"""
    results = {}
    
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        plates = [line.strip().upper() for line in lines if line.strip()]
        
        if verbose:
            print(f"Processando {len(plates)} placas do arquivo {batch_file}")
        
        for i, placa in enumerate(plates, 1):
            if verbose:
                print(f"[{i}/{len(plates)}] Consultando placa: {placa}")
            
            vehicle = cli.query_vehicle(placa, uf)
            
            if vehicle:
                results[placa] = vehicle.to_dict()
                if verbose:
                    print(f"  ✓ {placa}: {vehicle.marca} {vehicle.modelo}")
            else:
                results[placa] = {"error": "Veículo não encontrado ou erro na consulta"}
                if verbose:
                    print(f"  ✗ {placa}: Erro na consulta")
        
        return results
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{batch_file}' não encontrado", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Erro ao processar arquivo em lote: {e}", file=sys.stderr)
        return {}

def main():
    """Main CLI entry point"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.test_connection and not args.placa and not args.batch:
        parser.error("É necessário fornecer --placa, --batch ou --test-connection")
    
    # Criar CLI instance
    cli = VehicleQueryCLI(args.config)
    
    # Teste de conectividade
    if args.test_connection:
        if not args.quiet:
            print("Testando conectividade com o sistema DETRAN...")
        
        if cli.detran_service.login():
            print("✓ Conectividade OK")
            return 0
        else:
            print("✗ Falha na conectividade", file=sys.stderr)
            return 1
    
    # Processamento em lote
    if args.batch:
        results = process_batch_file(args.batch, cli, args.uf, args.verbose and not args.quiet)
        
        if not results:
            return 1
        
        # Formatar saída para lote
        if args.format == "json":
            output = json.dumps(results, indent=2, ensure_ascii=False)
        else:
            # Para lote, sempre usar JSON
            output = json.dumps(results, indent=2, ensure_ascii=False)
        
        # Salvar ou imprimir resultado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            if not args.quiet:
                print(f"Resultados salvos em: {args.output}")
        else:
            print(output)
        
        return 0
    
    # Consulta simples
    if args.verbose and not args.quiet:
        print(f"Consultando placa: {args.placa} (UF: {args.uf})")
    
    vehicle = cli.query_vehicle(args.placa, args.uf)
    
    if not vehicle:
        if not args.quiet:
            print("Veículo não encontrado ou erro na consulta", file=sys.stderr)
        return 1
    
    # Formatar saída
    output = cli.format_output(vehicle, args.format)
    
    # Salvar ou imprimir resultado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        if not args.quiet:
            print(f"Dados salvos em: {args.output}")
    else:
        print(output)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
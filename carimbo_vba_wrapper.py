#!/usr/bin/env python3
"""
CarimboPDF VBA Wrapper
======================

Este script é otimizado para ser chamado pelo Word VBA, fornecendo uma interface
simplificada e saída compatível com VBA para o sistema CarimboPDF.

Características especiais para VBA:
- Saída estruturada em JSON quando solicitada
- Códigos de saída específicos para diferentes tipos de erro
- Logging simplificado
- Tratamento robusto de caminhos Windows
- Validação de entrada otimizada

Uso:
    python carimbo_vba_wrapper.py --input arquivo.pdf --cidade "São Paulo" [opções]

"""

import sys
import json
import argparse
import traceback
from pathlib import Path
from datetime import date

# Adicionar o diretório src ao path se não estiver
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from data_hora_pdf.stamper import StampOptions, stamp_pdf

# Códigos de saída para VBA
EXIT_SUCCESS = 0
EXIT_FILE_NOT_FOUND = 1
EXIT_PYTHON_ERROR = 2
EXIT_INVALID_ARGS = 3
EXIT_PERMISSION_ERROR = 4
EXIT_UNKNOWN_ERROR = 5

def create_vba_result(success: bool, message: str, error_code: int = 0, file_path: str = "") -> dict:
    """Cria um resultado estruturado para o VBA."""
    return {
        "success": success,
        "message": message,
        "error_code": error_code,
        "file_path": file_path,
        "timestamp": date.today().isoformat()
    }

def validate_file_path(file_path: str) -> bool:
    """Valida se o caminho do arquivo existe e é acessível."""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except:
        return False

def sanitize_path(file_path: str) -> str:
    """Limpa e normaliza caminhos de arquivo para compatibilidade Windows/VBA."""
    try:
        # Remover aspas extras que podem vir do VBA
        file_path = file_path.strip('"\'')
        # Normalizar separadores para Windows
        file_path = file_path.replace("/", "\\")
        return str(Path(file_path).resolve())
    except:
        return file_path

def parse_args():
    """Configura e processa argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="CarimboPDF - Wrapper otimizado para Word VBA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Códigos de saída para VBA:
  0 - Sucesso
  1 - Arquivo não encontrado
  2 - Erro do Python/dependências
  3 - Argumentos inválidos
  4 - Erro de permissão
  5 - Erro desconhecido

Exemplos:
  python carimbo_vba_wrapper.py --input "C:\\docs\\arquivo.pdf" --cidade "São Paulo"
  python carimbo_vba_wrapper.py --input arquivo.pdf --in-place --cidade "Rio de Janeiro" --vba-output
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument("--input", required=True, help="Caminho do arquivo PDF de entrada")
    parser.add_argument("--cidade", required=True, help="Cidade para o carimbo")
    
    # Argumentos opcionais
    parser.add_argument("--output", help="Caminho do arquivo PDF de saída (opcional se --in-place)")
    parser.add_argument("--in-place", action="store_true", help="Sobrescrever arquivo original")
    parser.add_argument("--vba-output", action="store_true", help="Saída em formato JSON para VBA")
    
    # Opções de formatação
    parser.add_argument("--page", type=int, default=0, help="Página do carimbo (0 = primeira)")
    parser.add_argument("--font-size", type=float, default=12.0, help="Tamanho da fonte")
    parser.add_argument("--font", default="helv", help="Fonte (helv|times|cour)")
    parser.add_argument("--color", default="#000000", help="Cor em HEX")
    parser.add_argument("--bold", action="store_true", help="Negrito")
    parser.add_argument("--italic", action="store_true", help="Itálico")
    
    # Opções de logo
    parser.add_argument("--logo-path", help="Caminho do arquivo de logo")
    parser.add_argument("--logo-width-cm", type=float, default=2.0, help="Largura do logo em cm")
    parser.add_argument("--logo-margin-cm", type=float, default=0.5, help="Margem do logo em cm")
    
    # Opções de proteção
    parser.add_argument("--protection-password", help="Senha de proteção")
    parser.add_argument("--restrict-editing", action="store_true", help="Restringir edição")
    parser.add_argument("--no-copy", action="store_true", help="Desabilitar cópia")
    parser.add_argument("--encrypt-content", action="store_true", help="Criptografar conteúdo")
    
    # Data personalizada
    parser.add_argument("--date", help="Data personalizada (DD/MM/AAAA)")
    
    return parser.parse_args()

def main():
    """Função principal do wrapper VBA."""
    try:
        args = parse_args()
        
        # Sanitizar caminhos
        input_path = sanitize_path(args.input)
        output_path = sanitize_path(args.output) if args.output else None
        
        # Validar arquivo de entrada
        if not validate_file_path(input_path):
            result = create_vba_result(
                False, 
                f"Arquivo não encontrado ou inacessível: {input_path}",
                EXIT_FILE_NOT_FOUND
            )
            if args.vba_output:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"ERRO: {result['message']}")
            sys.exit(EXIT_FILE_NOT_FOUND)
        
        # Determinar arquivo de saída
        if args.in_place:
            final_output = input_path
        elif output_path:
            final_output = output_path
        else:
            # Gerar nome automático
            input_file = Path(input_path)
            final_output = str(input_file.with_name(f"{input_file.stem}_carimbado{input_file.suffix}"))
        
        # Configurar opções de carimbo
        options = StampOptions(
            page=args.page,
            font_size=args.font_size,
            font=args.font,
            color=args.color,
            bold=args.bold,
            italic=args.italic,
            logo_path=args.logo_path,
            logo_width_cm=args.logo_width_cm,
            logo_margin_cm=args.logo_margin_cm,
            protection_password=args.protection_password,
            restrict_editing=args.restrict_editing,
            allow_copy=not args.no_copy,
            encrypt_content=args.encrypt_content
        )
        
        # Processar data personalizada se fornecida
        custom_date = None
        if args.date:
            try:
                day, month, year = map(int, args.date.split('/'))
                custom_date = date(year, month, day)
                
                # Verificar se a data não é futura
                if custom_date > date.today():
                    raise ValueError("Data não pode ser futura")
                    
            except ValueError as e:
                result = create_vba_result(
                    False,
                    f"Data inválida '{args.date}': {str(e)}. Use formato DD/MM/AAAA",
                    EXIT_INVALID_ARGS
                )
                if args.vba_output:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print(f"ERRO: {result['message']}")
                sys.exit(EXIT_INVALID_ARGS)
        
        # Aplicar carimbo
        stamp_pdf(
            input_pdf=input_path,
            output_pdf=final_output,
            cidade=args.cidade,
            d=custom_date,
            options=options
        )
        
        # Verificar se o arquivo foi criado com sucesso
        if not validate_file_path(final_output):
            result = create_vba_result(
                False,
                f"Falha ao criar arquivo de saída: {final_output}",
                EXIT_UNKNOWN_ERROR
            )
            if args.vba_output:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"ERRO: {result['message']}")
            sys.exit(EXIT_UNKNOWN_ERROR)
        
        # Sucesso
        result = create_vba_result(
            True,
            f"Carimbo aplicado com sucesso em: {final_output}",
            EXIT_SUCCESS,
            final_output
        )
        
        if args.vba_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"SUCESSO: {result['message']}")
        
        sys.exit(EXIT_SUCCESS)
        
    except FileNotFoundError as e:
        result = create_vba_result(
            False,
            f"Arquivo não encontrado: {str(e)}",
            EXIT_FILE_NOT_FOUND
        )
        if args.vba_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"ERRO: {result['message']}")
        sys.exit(EXIT_FILE_NOT_FOUND)
        
    except PermissionError as e:
        result = create_vba_result(
            False,
            f"Erro de permissão: {str(e)}",
            EXIT_PERMISSION_ERROR
        )
        if args.vba_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"ERRO: {result['message']}")
        sys.exit(EXIT_PERMISSION_ERROR)
        
    except ImportError as e:
        result = create_vba_result(
            False,
            f"Dependência Python não encontrada: {str(e)}",
            EXIT_PYTHON_ERROR
        )
        if args.vba_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"ERRO: {result['message']}")
        sys.exit(EXIT_PYTHON_ERROR)
        
    except Exception as e:
        result = create_vba_result(
            False,
            f"Erro inesperado: {str(e)}",
            EXIT_UNKNOWN_ERROR
        )
        if args.vba_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"ERRO: {result['message']}")
            print(f"Detalhes técnicos:\n{traceback.format_exc()}")
        sys.exit(EXIT_UNKNOWN_ERROR)

if __name__ == "__main__":
    main()
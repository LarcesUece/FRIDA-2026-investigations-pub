import os
import platform

def obter_memoria_linux():
    """Lê o arquivo de sistema do Linux para descobrir a RAM total em GB."""
    try:
        with open('/proc/meminfo', 'r') as f:
            para_cada_linha = f.readlines()
            for linha in para_cada_linha:
                if 'MemTotal' in linha:
                    # O valor está em KB, vamos converter para GB
                    kb_memoria = int(linha.split()[1])
                    gb_memoria = kb_memoria / (1024 ** 2)
                    return round(gb_memoria, 2)
    except Exception:
        return "Desconhecido"

def rodar_diagnostico():
    print("="*40)
    print(" 🖥️  DIAGNÓSTICO DO DEVCONTAINER ")
    print("="*40)
    
    # Sistema Operacional
    print(f"📦 Sistema OS: {platform.system()} {platform.release()}")
    print(f"🐍 Versão Python: {platform.python_version()}")
    
    # Processamento (CPU)
    cpus = os.cpu_count()
    print(f"⚙️  Núcleos de CPU disponíveis: {cpus}")
    
    # Memória RAM
    ram_gb = obter_memoria_linux()
    print(f"🧠 Memória RAM Total: {ram_gb} GB")
    print("="*40)

    # Dica para o Benchmark
    print("\n💡 O que isso significa para o nosso Benchmark:")
    if isinstance(ram_gb, float):
        if ram_gb < 4.0:
            print("⚠️ ATENÇÃO: Você tem pouca RAM alocada para o Docker.")
            print("O Pandas e o Polars podem 'quebrar' com arquivos maiores que 500MB.")
            print("O Dask e o DuckDB serão os grandes heróis aqui!")
        elif ram_gb < 8.0:
            print("✅ RAM razoável. O teste de 1 Milhão de linhas vai rodar tranquilo.")
            print("O teste de 10 Milhões pode deixar o Pandas suando frio.")
        else:
            print("🚀 Máquina potente! Você tem RAM de sobra.")
            print("Vai ser uma briga boa de velocidade entre Polars e PyArrow.")

if __name__ == "__main__":
    rodar_diagnostico()
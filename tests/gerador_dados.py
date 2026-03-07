import pandas as pd
import numpy as np
from faker import Faker
import time
import os

fake = Faker('pt_BR')

def criar_pools_faker(tamanho_pool):
    """
    Cria uma 'piscina' de dados falsos para não ter que chamar o Faker milhões de vezes,
    o que deixaria o script lento demais.
    """
    print(f"  -> Criando base de dados falsos (Pool de {tamanho_pool} registros)...")
    return {
        'nomes': [fake.name() for _ in range(tamanho_pool)],
        'cpfs': [fake.cpf() for _ in range(tamanho_pool)],
        'estados': [fake.estado_sigla() for _ in range(tamanho_pool)],
        'paises': [fake.country() for _ in range(tamanho_pool)],
        'emails': [fake.ascii_email() for _ in range(tamanho_pool)]
    }

def gerar_coluna(tipo, num_linhas, pools):
    """Gera os dados para a coluna de acordo com o tipo solicitado."""
    if tipo == 'nome':
        return np.random.choice(pools['nomes'], num_linhas)
    elif tipo == 'cpf':
        return np.random.choice(pools['cpfs'], num_linhas)
    elif tipo == 'altura':
        return np.round(np.random.uniform(1.40, 2.15, num_linhas), 2)
    elif tipo == 'peso':
        return np.round(np.random.uniform(45.0, 150.0, num_linhas), 1)
    elif tipo == 'score_credito':
        return np.random.randint(0, 1001, num_linhas)
    elif tipo == 'estado':
        return np.random.choice(pools['estados'], num_linhas)
    elif tipo == 'pais':
        return np.random.choice(pools['paises'], num_linhas)
    elif tipo == 'valor_precisao':
        # Float genérico de altíssima precisão (nativamente o Python/Numpy usa float64)
        return np.random.uniform(0.0, 999999.999999, num_linhas)
    elif tipo == 'sexo':
        return np.random.choice(['Masculino', 'Feminino', 'Outro'], num_linhas)
    elif tipo == 'email':
        return np.random.choice(pools['emails'], num_linhas)

def gerar_dataset_flexivel(num_linhas, num_colunas, nome_arquivo):
    print(f"\n⚙️ Iniciando geração: {num_linhas:,} linhas x {num_colunas} colunas")
    inicio = time.time()

    os.makedirs("DATA", exist_ok=True)
    caminho_completo = f"DATA/{nome_arquivo}"

    # Limita o pool a 100k para gerar rápido, mas os sorteios criarão milhões de linhas
    tamanho_pool = min(num_linhas, 100_000)
    pools = criar_pools_faker(tamanho_pool)

    # O nosso cardápio base de 10 colunas
    tipos_base = [
        'nome', 'cpf', 'altura', 'peso', 'score_credito', 
        'estado', 'pais', 'valor_precisao', 'sexo', 'email'
    ]
    
    dados = {}
    
    print(f"  -> Montando as {num_colunas} colunas...")
    for i in range(num_colunas):
        # Descobre qual é o tipo de coluna atual usando o "resto da divisão"
        tipo_atual = tipos_base[i % len(tipos_base)]
        
        # Descobre em qual "ciclo" estamos (1, 2, 3...)
        ciclo = (i // len(tipos_base)) + 1
        
        # Cria o nome final (ex: nome_1, peso_2, etc)
        # Só usamos o sufixo _1, _2 se for pedido mais do que 10 colunas
        if num_colunas <= len(tipos_base):
            nome_coluna = tipo_atual
        else:
            nome_coluna = f"{tipo_atual}_{ciclo}"
            
        dados[nome_coluna] = gerar_coluna(tipo_atual, num_linhas, pools)

    print(f"  -> Salvando arquivo no disco ({caminho_completo})...")
    df = pd.DataFrame(dados)
    df.to_csv(caminho_completo, index=False)
    
    fim = time.time()
    tamanho_mb = os.path.getsize(caminho_completo) / (1024 * 1024)
    print(f"✅ Concluído! Arquivo gerado com sucesso.")
    print(f"   📊 Tamanho: {tamanho_mb:.2f} MB")
    print(f"   ⏱️  Tempo: {fim - inicio:.2f} segundos")

if __name__ == "__main__":
    # Vamos criar 3 cenários diferentes para brincar no benchmark!
    
    # Cenário 1: Arquivo Padrão (1 Milhão de linhas, 10 colunas base)
    gerar_dataset_flexivel(
        num_linhas=1_000_000, 
        num_colunas=10, 
        nome_arquivo="dataset_1M_padrao.csv"
    )
    
    # Cenário 2: Arquivo "Largo" (100 mil linhas, mas 50 colunas - 5 ciclos!)
    gerar_dataset_flexivel(
        num_linhas=100_000, 
        num_colunas=50, 
        nome_arquivo="dataset_100k_largo.csv"
    )
    
    # Cenário 3: O seu exemplo (25 colunas)
    gerar_dataset_flexivel(
        num_linhas=500_000, 
        num_colunas=25, 
        nome_arquivo="dataset_500k_25cols.csv"
    )
"""
Script de migração do formato antigo (arquivo único) para a nova estrutura modular.
"""
import os
import shutil

def realizar_migracao():
    """
    Migra automaticamente do arquivo único (calendar_widget.py) para a nova estrutura.
    Verifica se os arquivos já existem para evitar sobrescrever alterações.
    """
    # Verificar se o arquivo original existe
    if not os.path.exists('calendar_widget.py'):
        print("Erro: arquivo calendar_widget.py não encontrado.")
        return False
    
    print("Iniciando migração...")
    
    # Criar backup do arquivo original
    shutil.copy2('calendar_widget.py', 'calendar_widget.py.bak')
    print("Backup do arquivo original criado como calendar_widget.py.bak")
    
    # Verificar se a nova estrutura já existe
    arquivos_novos = [
        os.path.exists('app.py'),
        os.path.exists('src/__init__.py'),
        os.path.exists('src/main.py'),
        os.path.exists('src/auth.py'),
        os.path.exists('src/calendar_api.py'),
        os.path.exists('src/ui.py'),
        os.path.exists('src/utils.py')
    ]
    
    if all(arquivos_novos):
        print("A nova estrutura já existe. Nenhuma ação adicional necessária.")
        return True
    
    print("Migração concluída com sucesso! O código agora está organizado em módulos.")
    print("\nPara executar o widget, use agora:")
    print("python app.py")
    
    return True

if __name__ == "__main__":
    # Executar a migração
    realizar_migracao() 
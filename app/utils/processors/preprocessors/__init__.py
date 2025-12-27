"""
Pacote de preprocessadores para arquivos especiais

Preprocessadores tratam arquivos com formatos não-padronizados antes
de passar para o sistema de detecção automática.

Versão: 1.0.0
"""

from .extrato_itau_xls import is_extrato_itau_xls, preprocessar_extrato_itau_xls

__all__ = [
    'is_extrato_itau_xls',
    'preprocessar_extrato_itau_xls',
]

"""
Serviço de Paginação - Gerencia lógica de paginação para listas.
Código movido do app.py para organizar responsabilidades.
"""

from math import ceil


def paginate_items(items, page, per_page=12):
    """
    Aplica paginação a uma lista de itens.

    Args:
        items: Lista de itens para paginar
        page: Número da página atual
        per_page: Itens por página (padrão: 12)

    Returns:
        dict: {
            'items': Lista paginada de itens,
            'page': Página atual,
            'total_pages': Total de páginas,
            'total': Total de itens
        }
    """
    total = len(items)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    items_paginados = items[start:end]

    return {
        'items': items_paginados,
        'page': page,
        'total_pages': total_pages,
        'total': total
    }


def get_pagination_data(page, total_items, per_page=12):
    """
    Calcula dados de paginação sem aplicar a paginação.
    Útil quando você quer apenas os metadados de paginação.

    Args:
        page: Número da página atual
        total_items: Total de itens
        per_page: Itens por página (padrão: 12)

    Returns:
        dict: {
            'page': Página atual,
            'total_pages': Total de páginas,
            'total': Total de itens,
            'start': Índice de início,
            'end': Índice de fim
        }
    """
    total_pages = ceil(total_items / per_page)
    start = (page - 1) * per_page
    end = start + per_page

    return {
        'page': page,
        'total_pages': total_pages,
        'total': total_items,
        'start': start,
        'end': end
    }

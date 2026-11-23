from items.models import Item


def make_item(author, **fields):
    """Creates an open found item for the tests; pass fields to override the defaults."""
    defaults = {
        'kind': Item.Kind.FOUND,
        'title': 'Garrafa verde',
        'description': 'Encontrada na sala 2015 do ICEx',
        'category': Item.Category.BOTTLES,
        'location': Item.Location.ICEX,
    }
    defaults.update(fields)
    return Item.objects.create(author=author, **defaults)

bl_info = {
    "name": "LED Tree Importer/Exporter",
    "author": "ambiguousname",
    "blender": (3, 0, 0),
    "version": (1, 0, 0),
    "support": 'COMMUNITY',
    "description": "Import a .CSV of positions, export as a .CSV of colors at different frames",
    "warning": "With the exception of importing the LED tree, you should have the tree selected when importing/exporting data.",
    "wiki_url": "https://github.com/ambiguousname/ParkerTreeBlenderAddOn",
    "category": "Import-Export",
}

from . import animationpreview
from . import tree_importer_exporter

modules = [
    animationpreview,
    tree_importer_exporter
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in modules:
        module.unregister()

if __name__ == '__main__':
    register()
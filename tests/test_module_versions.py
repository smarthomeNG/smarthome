"""
The version of every module in module.yaml equals the ``version`` of its class.

``lib.module.Modules`` does not start a module whose code version differs from its metadata version.
"""

import ast
import tempfile
import unittest
from pathlib import Path

from ruamel.yaml import YAML

MODULES_DIR = Path(__file__).resolve().parent.parent / 'modules'


def metadata_of(module_dir: Path) -> dict:
    """The ``module`` section of the module's module.yaml."""
    return YAML(typ='safe').load((module_dir / 'module.yaml').read_text(encoding='utf-8'))['module']


def class_version(init_file: Path, classname: str) -> str | None:
    """
    The string assigned to ``version`` in the body of class *classname* of *init_file*

    :return: the version, or None if the class or the assignment does not exist
    """
    for node in ast.parse(init_file.read_text(encoding='utf-8')).body:
        if isinstance(node, ast.ClassDef) and node.name == classname:
            for statement in node.body:
                if isinstance(statement, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == 'version' for target in statement.targets
                ):
                    return ast.literal_eval(statement.value)
    return None


def module_dirs() -> list[Path]:
    """The directories of the modules that have a module.yaml."""
    return sorted(path.parent for path in MODULES_DIR.glob('*/module.yaml'))


class TestModuleVersions(unittest.TestCase):
    def test_code_version_equals_metadata_version(self):
        checked = []
        for module_dir in module_dirs():
            meta = metadata_of(module_dir)
            classname = meta['classname']
            init_file = module_dir / '__init__.py'
            if classname == 'None' or classname is None or not init_file.is_file():
                continue  # metadata without code (e.g. modules/core)
            with self.subTest(module=module_dir.name):
                self.assertEqual(str(meta['version']), class_version(init_file, classname))
            checked.append(module_dir.name)

        self.assertIn('http', checked)

    def test_class_version_reads_the_class_body_only(self):
        source = "version = '9.9.9'\n\nclass Other:\n    version = '1.0.0'\n\nclass Wanted:\n    version = '2.0.0'\n"
        with tempfile.TemporaryDirectory() as tmp:
            init_file = Path(tmp) / '__init__.py'
            init_file.write_text(source, encoding='utf-8')

            self.assertEqual('2.0.0', class_version(init_file, 'Wanted'))
            self.assertIsNone(class_version(init_file, 'Missing'))


if __name__ == '__main__':
    unittest.main()

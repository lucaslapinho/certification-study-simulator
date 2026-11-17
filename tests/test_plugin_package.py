"""Regression for the ChatGPT New Plugin archive layout."""
import copy
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import package


class PluginPackageTest(unittest.TestCase):
    def test_import_paths_and_canonical_skill_files(self):
        runtime_files = package.files(package.SKILL)
        _, entries = package.plugin_entries(runtime_files)
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / 'plugin.zip'
            package.archive(archive_path, entries)
            with zipfile.ZipFile(archive_path) as archive:
                manifest_path = '.codex-plugin/plugin.json'
                icon_path = 'assets/certification-study-simulator.png'
                skill_directory = 'skills/certification-study-simulator/'
                expected_skill_paths = {
                    skill_directory + path.relative_to(package.SKILL).as_posix(): path
                    for path in runtime_files
                }
                self.assertEqual(set(archive.namelist()), {manifest_path, icon_path, *expected_skill_paths})
                self.assertIsNone(archive.testzip())

                manifest = json.loads(archive.read(manifest_path))
                self.assertEqual(manifest['name'], 'certification-study-simulator')
                self.assertRegex(manifest['version'], r'^\d+\.\d+\.\d+$')
                self.assertTrue(manifest['description'].strip())
                self.assertEqual(manifest['skills'], './skills/')
                self.assertEqual(
                    manifest['interface']['displayName'],
                    'Certification Teacher & Exam Simulator',
                )
                self.assertEqual(manifest['interface']['logo'], f'./{icon_path}')
                self.assertEqual(manifest['interface']['composerIcon'], f'./{icon_path}')
                self.assertEqual(archive.read(icon_path), (package.PLUGIN_ROOT / icon_path).read_bytes())

                skill_markdown = archive.read(skill_directory + 'SKILL.md').decode('utf-8')
                frontmatter = yaml.safe_load(skill_markdown.split('---', 2)[1])
                self.assertEqual(frontmatter['name'], manifest['name'])
                for archive_name, source_path in expected_skill_paths.items():
                    with self.subTest(path=archive_name):
                        self.assertEqual(archive.read(archive_name), source_path.read_bytes())

    def test_rejects_absent_or_whitespace_long_description(self):
        original = json.loads(package.PLUGIN_MANIFEST.read_text(encoding='utf-8'))
        for value in (None, '', '  \n ', 42, 'x' * 4001):
            with self.subTest(value_type=type(value).__name__, value_length=len(str(value))):
                manifest = copy.deepcopy(original)
                if value is None:
                    del manifest['interface']['longDescription']
                else:
                    manifest['interface']['longDescription'] = value
                with self.assertRaisesRegex(ValueError, r'interface\.longDescription'):
                    package.validate_plugin_manifest(manifest, package.PLUGIN_ROOT)

    def test_rejects_missing_publisher_and_capabilities(self):
        original = json.loads(package.PLUGIN_MANIFEST.read_text(encoding='utf-8'))
        for section, key in [('author', 'name'), ('interface', 'developerName'), ('interface', 'capabilities')]:
            with self.subTest(field=f'{section}.{key}'):
                manifest = copy.deepcopy(original)
                del manifest[section][key]
                with self.assertRaisesRegex(ValueError, rf'{section}\.{key}'):
                    package.validate_plugin_manifest(manifest, package.PLUGIN_ROOT)

    def test_rejects_missing_icon_and_paths_outside_archive(self):
        original = json.loads(package.PLUGIN_MANIFEST.read_text(encoding='utf-8'))
        for key in ('logo', 'composerIcon'):
            for path in ('./assets/missing.png', './../icon.png'):
                with self.subTest(field=key, path=path):
                    manifest = copy.deepcopy(original)
                    manifest['interface'][key] = path
                    with self.assertRaisesRegex(ValueError, rf'interface\.{key}'):
                        package.validate_plugin_manifest(manifest, package.PLUGIN_ROOT)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Build Skill or plugin ZIPs from the canonical source."""
import argparse
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'source/certification-study-simulator'
PLUGIN_ROOT=ROOT/'plugin'
PLUGIN_MANIFEST=PLUGIN_ROOT/'.codex-plugin/plugin.json'
RELEASE_VERSION = re.compile(r'(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}')
PLUGIN_CATEGORIES = {
    'Productivity', 'Creativity', 'Developer Tools', 'Business & Operations',
    'Data & Analytics', 'Communication', 'Education & Research', 'Security',
    'Finance', 'Healthcare', 'Travel', 'Entertainment', 'Other',
}

def files(root):
    result=[]
    for p in sorted(root.rglob('*')):
        if '__pycache__' in p.parts or p.suffix=='.pyc': continue
        if p.is_symlink(): raise ValueError('Symlink não permitido: '+str(p))
        if p.is_file(): result.append(p)
    return result

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def archive(path,entries):
    seen=set()
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for source,name in sorted(entries,key=lambda x:x[1]):
            if name in seen or name.startswith('/') or '..' in Path(name).parts: raise ValueError('Nome inseguro/duplicado')
            seen.add(name)
            info=zipfile.ZipInfo(name,date_time=(2026,11,16,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            z.writestr(info,source.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError('CRC inválido')
        for source,name in entries:
            if z.read(name) != source.read_bytes(): raise ValueError('Bytes divergem')

def required_text(value, field, maximum, multiline=False):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} é obrigatório e deve conter texto.')
    if len(value) > maximum:
        raise ValueError(f'{field} ultrapassa {maximum} caracteres.')
    if any(not char.isprintable() for char in value if not (multiline and char == '\n')):
        raise ValueError(f'{field} contém caracteres de controle ou quebras de linha inválidas.')
    return value


def png_asset(root, value, field):
    path_text = required_text(value, field, 2048)
    relative = PurePosixPath(path_text[2:])
    if not path_text.startswith('./') or '\\' in path_text or relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'{field} deve apontar para um arquivo relativo à raiz do plugin.')
    path = root / relative
    if not path.is_file() or path.resolve() != root.resolve() / relative:
        raise ValueError(f'{field} aponta para um arquivo ausente ou um link: {path_text}')
    if path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError(f'{field} ultrapassa 5 MiB.')
    with path.open('rb') as image_file:
        header = image_file.read(24)
    if path.suffix.lower() != '.png' or len(header) != 24 or header[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
        raise ValueError(f'{field} deve apontar para o PNG de distribuição deste projeto.')
    width, height = struct.unpack('>II', header[16:])
    if width != height or not 48 <= width <= 4096:
        raise ValueError(f'{field} deve ser quadrado e medir entre 48 e 4096 px.')
    return path


def validate_plugin_manifest(manifest, root):
    """Check the Codex manifest fields used by this skills-only upload."""
    if not isinstance(manifest, dict):
        raise ValueError('O manifesto deve ser um objeto JSON.')
    if manifest.get('name') != SKILL.name:
        raise ValueError('Nome do plugin diverge do identificador da Skill.')
    version = required_text(manifest.get('version'), 'version', 64)
    if not RELEASE_VERSION.fullmatch(version):
        raise ValueError('version deve usar o formato MAJOR.MINOR.PATCH.')
    required_text(manifest.get('description'), 'description', 1024, multiline=True)
    author = manifest.get('author')
    if not isinstance(author, dict):
        raise ValueError('author deve ser um objeto JSON.')
    required_text(author.get('name'), 'author.name', 120)
    if manifest.get('skills') != './skills/':
        raise ValueError('skills deve apontar para ./skills/.')

    interface = manifest.get('interface')
    if not isinstance(interface, dict):
        raise ValueError('interface deve ser um objeto JSON.')
    required_text(interface.get('displayName'), 'interface.displayName', 80)
    required_text(interface.get('shortDescription'), 'interface.shortDescription', 240)
    required_text(interface.get('longDescription'), 'interface.longDescription', 4000, multiline=True)
    required_text(interface.get('developerName'), 'interface.developerName', 120)
    category = required_text(interface.get('category'), 'interface.category', 80)
    if category not in PLUGIN_CATEGORIES:
        raise ValueError('interface.category deve usar uma categoria reconhecida.')

    capabilities = interface.get('capabilities')
    if not isinstance(capabilities, list) or len(capabilities) > 20:
        raise ValueError('interface.capabilities deve ser uma lista com até 20 itens.')
    for index, value in enumerate(capabilities):
        required_text(value, f'interface.capabilities[{index}]', 120)
    if 'defaultPrompt' in interface:
        prompts = interface['defaultPrompt']
        if isinstance(prompts, str):
            prompts = [prompts]
        if not isinstance(prompts, list) or len(prompts) > 3:
            raise ValueError('interface.defaultPrompt deve ter até três sugestões.')
        for index, value in enumerate(prompts):
            required_text(value, f'interface.defaultPrompt[{index}]', 512)

    return {
        png_asset(root, interface.get(key), f'interface.{key}')
        for key in ('logo', 'composerIcon')
    }


def plugin_entries(runtime_files):
    """Build the Codex compatibility layout for the ChatGPT archive importer."""
    manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding='utf-8'))
    assets = validate_plugin_manifest(manifest, PLUGIN_ROOT)
    if not (SKILL / 'SKILL.md').is_file():
        raise ValueError('A Skill precisa conter SKILL.md.')
    entries = [(PLUGIN_MANIFEST, '.codex-plugin/plugin.json')]
    entries.extend((path, path.relative_to(PLUGIN_ROOT).as_posix()) for path in sorted(assets))
    skill_root = f'skills/{SKILL.name}'
    for path in runtime_files:
        relative_path = path.relative_to(SKILL).as_posix()
        entries.append((path, f'{skill_root}/{relative_path}'))
    return manifest, entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--plugin', action='store_true', help='Empacota para New Plugin no ChatGPT.')
    args = parser.parse_args()
    if not RELEASE_VERSION.fullmatch(args.version):
        parser.error('Versão inválida.')

    skill_version = (ROOT/'VERSION').read_text().strip()
    runtime = files(SKILL)
    if any('tests' in path.relative_to(SKILL).parts for path in runtime):
        parser.error('Testes não pertencem ao runtime.')
    if args.plugin:
        try:
            plugin_manifest, runtime_entries = plugin_entries(runtime)
        except (ValueError, OSError) as error:
            parser.error(str(error))
        expected_version = plugin_manifest.get('version')
        package_kind = 'plugin'
        package_type = 'Plugin archive for ChatGPT using the Codex compatibility manifest'
    else:
        expected_version = skill_version
        package_kind = 'skill'
        package_type = 'Standalone Skill files distribution'
        runtime_entries = [
            (path, f'{SKILL.name}/{path.relative_to(SKILL).as_posix()}')
            for path in runtime
        ]
    if args.version != expected_version:
        parser.error(f'A versão solicitada diverge da versão declarada: {expected_version}.')

    destination = ROOT/'packages'/args.version
    destination.mkdir(parents=True,exist_ok=False)
    runtime_zip = destination/f'{SKILL.name}-{args.version}-{package_kind}.zip'
    sourcezip=destination/f'{SKILL.name}-{args.version}-source.zip'
    archive(runtime_zip, runtime_entries)
    dev=[ROOT/x for x in ['README.md','VERSION','CHANGELOG.md']]
    for folder in ['source','plugin','docs','tests','tools','evidence']: dev+=files(ROOT/folder)
    archive(sourcezip,[(x,'certification-study-simulator-project/'+x.relative_to(ROOT).as_posix()) for x in dev])
    manifest={'version':args.version,'skill_version':skill_version,'skill_files':{x.relative_to(SKILL).as_posix():sha(x) for x in runtime},
              'archives':{x.name:sha(x) for x in [runtime_zip,sourcezip]},
              'checks':{'crc':'PASS','unique_safe_paths':'PASS','canonical_byte_equivalence':'PASS','no_symlinks':'PASS','evaluation_material_excluded_from_skill':'PASS'},
              'import':'NOT RUN','package_type':{package_kind:package_type,'source':'development source'}}
    if args.plugin:
        manifest['checks']['codex_manifest_metadata_and_assets'] = 'PASS'
    (destination/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (destination/'SHA256SUMS.txt').write_text(''.join(sha(x)+'  '+x.name+'\n' for x in [runtime_zip,sourcezip]))
    print(json.dumps({'runtime_file_count':len(runtime),'development_file_count':len(dev),'checks':manifest['checks'],'archives':manifest['archives']},ensure_ascii=False,indent=2))

if __name__=='__main__': main()

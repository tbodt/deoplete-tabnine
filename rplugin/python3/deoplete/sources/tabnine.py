import json
import re
import os
import platform
import subprocess

from deoplete.source.base import Base
from deoplete.util import getlines

LSP_KINDS = [
    'Text',
    'Method',
    'Function',
    'Constructor',
    'Field',
    'Variable',
    'Class',
    'Interface',
    'Module',
    'Property',
    'Unit',
    'Value',
    'Enum',
    'Keyword',
    'Snippet',
    'Color',
    'File',
    'Reference',
    'Folder',
    'EnumMember',
    'Constant',
    'Struct',
    'Event',
    'Operator',
    'TypeParameter',
]


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'tabnine'
        self.mark = '[TN]'
        self.rank = 1000
        self.matchers = []
        self.sorters = []
        self.converters = [
            'converter_remove_overlap',
            'converter_truncate_info',
        ]
        self.min_pattern_length = 1
        self.is_volatile = True
        self.input_pattern = r'[^\w\s]$|TabNine::\w*$'
        self.vars = {
            'line_limit': 1000,
            'max_num_results': 10,
        }

        self._proc = None
        self._response = None
        self._install_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

    def get_complete_position(self, context):
        m = re.search(r'\s+$', context['input'])
        if m:
            return -1

        self._response = self._get_response(context)
        if self._response is None or 'old_prefix' not in self._response:
            return -1

        old_prefix = self._response['old_prefix']
        if not context['input'].endswith(old_prefix):
            return -1
        return len(context['input']) - len(old_prefix)

    def gather_candidates(self, context):
        if self._response is None or 'results' not in self._response:
            return []

        response = self._response
        if 'promotional_message' in response:
            self.print(' '.join(response['promotional_message']))
        candidates = []
        for result in response['results']:
            candidate = {'word': result['new_prefix']}
            if result['old_suffix'] or result['new_suffix']:
                candidate['user_data'] = json.dumps({
                    'old_suffix': result['old_suffix'],
                    'new_suffix': result['new_suffix'],
                })
            if result.get('detail'):
                candidate['menu'] = result['detail']
            if result.get('deprecated'):
                candidate['menu'] = 'deprecated'
            if result.get('documentation'):
                doc = result['documentation']
                candidate['info'] = (doc.get('value', '')
                                     if isinstance(doc, dict) else doc)
            if result.get('kind'):
                candidate['kind'] = LSP_KINDS[result['kind'] - 1]
            candidates.append(candidate)
        return candidates

    def _get_response(self, context):
        limit = self.get_var('line_limit')
        _, line, col, _ = self.vim.call('getpos', '.')
        last_line = self.vim.call('line', '$')
        before_line = max(1, line - limit)
        before_lines = getlines(self.vim, before_line, line)
        if before_lines:
            before_lines[-1] = before_lines[-1][:col-1]
        after_line = min(last_line, line + limit)
        after_lines = getlines(self.vim, line, after_line)
        if after_lines:
            after_lines[0] = after_lines[0][col:]
        return self._request(
            'Autocomplete',
            filename=context['bufpath'],
            before='\n'.join(before_lines),
            after='\n'.join(after_lines),
            region_includes_beginning=(before_line == 1),
            region_includes_end=(after_line == last_line),
            max_num_results=self.get_var('max_num_results'),
        )

    def _request(self, name, **params):
        req = {
            'version': '1.0.14',
            'request': {name: params}
        }
        self.debug(repr(req))
        proc = self._get_running_tabnine()
        if proc is None:
            return

        try:
            json.dump(req, proc.stdin, ensure_ascii=False, check_circular=False)
            proc.stdin.write('\n')
            proc.stdin.flush()
        except BrokenPipeError:
            self._restart()
            return

        output = proc.stdout.readline()
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            self.debug('Tabnine output is corrupted: ' + output)

    def _restart(self):
        if self._proc is not None:
            self._proc.terminate()
            self._proc = None
        binary_dir = os.path.join(self._install_dir, 'binaries')
        path = get_tabnine_path(binary_dir)
        if path is None:
            self.print_error('no TabNine binary found')
            return
        self._proc = subprocess.Popen(
            [path, '--client', 'sublime', '--log-file-path',
             os.path.join(self._install_dir, 'tabnine.log')],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
        )

    def _get_running_tabnine(self):
        if self._proc is None:
            self._restart()
        if self._proc is not None and self._proc.poll():
            self.print_error(
                'TabNine exited with code {}'.format(self._proc.returncode))
            self._restart()
        return self._proc


# Adapted from the sublime plugin
def parse_semver(s):
    try:
        return [int(x) for x in s.split('.')]
    except ValueError:
        return []


def get_tabnine_path(binary_dir):
    SYSTEM_MAPPING = {
        'Darwin': 'apple-darwin',
        'Linux': 'unknown-linux-gnu',
        'Windows': 'pc-windows-gnu'
    }
    versions = os.listdir(binary_dir)
    versions.sort(key=parse_semver, reverse=True)
    for version in versions:
        triple = '{}-{}'.format(parse_architecture(platform.machine()),
                                SYSTEM_MAPPING[platform.system()])
        path = os.path.join(binary_dir, version, triple,
                            executable_name('TabNine'))
        if os.path.isfile(path):
            return path


def parse_architecture(arch):
    if arch == 'AMD64':
        return 'x86_64'
    else:
        return arch


def executable_name(name):
    if platform.system() == 'Windows':
        return name + '.exe'
    else:
        return name

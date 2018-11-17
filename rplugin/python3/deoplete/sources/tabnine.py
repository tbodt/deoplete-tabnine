import json
import os
import platform
import subprocess

from deoplete.source.base import Base
from deoplete.util import getlines


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'tabnine'
        self.mark = '[TN]'
        self.rank = 1000
        self.proc = None
        self.matchers = []
        self.sorters = []
        self.converters = []
        self.min_pattern_length = 1
        self.is_debug_enabled = True
        self.is_volatile = True

        self._install_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

    def gather_candidates(self, context):
        LINE_LIMIT = 1000
        _, line, col, _ = context['position']
        last_line = self.vim.call('line', '$')
        before_line = max(1, line - LINE_LIMIT)
        before_lines = getlines(self.vim, before_line, line)
        before_lines[-1] = before_lines[-1][:col-1]
        after_line = min(last_line, line + LINE_LIMIT)
        after_lines = getlines(self.vim, line, after_line)
        after_lines[0] = after_lines[0][col:]
        response = self.request(
            'Autocomplete',
            filename=context['bufpath'],
            before='\n'.join(before_lines),
            after='\n'.join(after_lines),
            region_includes_beginning=(before_line == 1),
            region_includes_end=(after_line == last_line),
            max_num_results=10,
        )
        if response is None:
            return []

        if response['promotional_message']:
            self.print(' '.join(response['promotional_message']))
        candidates = []
        self.debug(repr(response))
        for result in response['results']:
            candidate = {}
            word = result['result']
            prefix_to_substitute = result['prefix_to_substitute']
            candidate['word'] = word
            if word.endswith(prefix_to_substitute):
                candidate['word'] = word[:len(word)-len(prefix_to_substitute)]
                candidate['abbr'] = word
            candidates.append(candidate)
        self.debug(repr(candidates))
        return candidates

    def request(self, name, **params):
        req = {
            'version': '0.6.0',
            'request': {name: params}
        }
        self.debug(repr(req))
        proc = self.get_running_tabnine()
        if proc is None:
            return
        proc.stdin.write((json.dumps(req) + '\n').encode('utf8'))
        proc.stdin.flush()
        return json.loads(proc.stdout.readline().decode('utf8'))

    def restart(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc = None
        binary_dir = os.path.join(self._install_dir, 'binaries')
        path = get_tabnine_path(binary_dir)
        if path is None:
            self.print_error('no TabNine binary found')
            return
        self.proc = subprocess.Popen(
            [path, '--client', 'sublime', '--log-file-path',
             os.path.join(self._install_dir, 'tabnine.log')],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def get_running_tabnine(self):
        if self.proc is None:
            self.restart()
        if self.proc is not None and self.proc.poll():
            self.print_error(
                'TabNine exited with code {}'.format(self.proc.returncode))
            self.restart()
        return self.proc


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
        path = os.path.join(binary_dir, version, triple, executable_name('TabNine'))
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

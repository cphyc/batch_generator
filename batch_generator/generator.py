import argparse
import appdirs
import os
from os import path
from glob import glob
import sys
import re
import logging

from .backends import detect_backend

from .log import logger
TEMPLATE_re = re.compile(r'{{([^}]+)}}')
DTYPES = {'int': int, 'float': float, 'str': str}


class CmdLineHandler():
    def __init__(self):
        self.parse_cmd_args()
        self.set_backend()

    def create_dirs(self):
        self.data_dir = appdirs.user_data_dir('batch_generator')
        self.config_dir = appdirs.user_data_dir('batch_generator')

        for d in [self.data_dir, self.config_dir]:
            if not path.isdir(d):
                logger.debug('Creating directory %s' % d)
                os.makedirs(d)
            else:
                logger.debug('Found directory %s' % d)

    def set_backend(self):
        '''Detect and set the backend to use.'''
        backend = detect_backend()

        logger.debug('Using backend %s' % backend)

        self.backend = backend

    def ask(self, question, default=None, dtype=None, ans_ok=None):
        '''Ask a question to the user.'''

        def cast(e):
            if default and e.strip() == '':
                return dtype(default)
            elif dtype:
                return dtype(e)
            else:
                return e

        ok = False
        while not ok:
            if default:
                q = '%s [%s]' % (question, default)
            else:
                q = '%s' % question

            # Add question mark/colon
            if not (q.endswith('?') or q.endswith(':')):
                q += ':'

            # Add trailing whitespace
            q += ' '
            ret = input(q)
            try:
                cret = cast(ret)
                if ans_ok is None:
                    ok = True
                elif callable(ans_ok):
                    ok = ans_ok(cret)
                else:
                    ok = cret in ans_ok
            except ValueError:
                ok = False

            if not ok:
                print('Invalid answer! ', end='')

        return cret

    def generate_template(self, template):
        with open(template, 'r') as f:
            lines = f.readlines()

        # Populate data
        data = dict(
            cwd=path.abspath(path.curdir),
        )

        # Loop over lines, prompting the user whenever an element is found
        answers = []

        for line in lines:
            elements = TEMPLATE_re.findall(line)
            if len(elements) == 0:
                continue

            for el in elements:
                chunks = el.split('|')
                # 1 chunk:  computed (automatic)
                # 2 chunks: name, help
                # 3 chunks: name, help, default
                get_input = True
                store_data = True
                if len(chunks) == 1:
                    ans = eval(chunks[0], data.copy())
                    name = 'automatic'
                    store_data = False
                    get_input = False
                elif len(chunks) == 2:
                    tmp, help = chunks
                    name, dtype = tmp.split(':')
                    default = None
                elif len(chunks) == 3:
                    tmp, help, default = chunks
                    name, dtype = tmp.split(':')

                if default and default.startswith('eval:'):
                    default = eval(default.split('eval:')[1], data.copy())

                if get_input:
                    ans = self.ask(help,
                                   default=default,
                                   dtype=DTYPES[dtype])
                answers.append(ans)
                if store_data:
                    data[name] = ans
                logger.debug('Got %s for %s' % (ans, name))

        # Not create filled_template
        newLines = []
        start = 0
        lines = ''.join(lines)
        for ans in answers:
            match = TEMPLATE_re.search(lines, start)
            beg, end = match.span()
            newLines.append(lines[start:beg])
            newLines.append(str(ans))
            start = end

        newLines.append(lines[start:])

        newLines = ''.join(newLines)
        return newLines

    def generate(self, args):
        '''Generate a batch file.'''
        template_dir = self.data_dir
        templates = glob(
            path.join(
                template_dir,
                '%(backend)s.*' % dict(backend=self.backend)
                )
            )

        if len(templates) == 0:
            errmsg = ('You need to setup a template first.\nTemplates '
                      'are stored in "%s" and have the format "%s".')
            logger.error(errmsg % (template_dir,
                                     '%s.SOMENAME' % self.backend))
            sys.exit(1)

        elif len(templates) == 1:
            content = self.generate_template(templates[0])
        else:
            for i, template in enumerate(templates):
                print('%2d: %s' % (i, template))

            ans_ok = list(range(len(templates)))
            ans = self.ask('Which template to use?', dtype=int, ans_ok=ans_ok)

            content = self.generate_template(templates[ans])

        with open(args.output, 'w') as f:
            f.write(content)

        logger.info('Wrote %s', args.output)

    def run(self, args):
        self.handler.run(args.file)

    def stat(self, args):
        pass

    def parse_cmd_args(self):
        parser = argparse.ArgumentParser(description='Generate, run and track jobs in a unified way.')
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Be verbose.')
        parser.set_defaults(func=None)
        sparsers = parser.add_subparsers()

        gen_parser = sparsers.add_parser('generate', aliases=['g'],
                                         help='Generate batch jobs.')
        gen_parser.set_defaults(func=self.generate)
        gen_parser.add_argument('output', nargs='?',
                                help='Name of the file to generate'
                                ' (default: %(default)s).',
                                default='job.sh')

        run_parser = sparsers.add_parser('run', aliases=['r'],
                                         help='Run a batch job.')
        run_parser.add_argument('file', help='The file to run.')

        run_parser.set_defaults(func=self.run)

        stat_parser = sparsers.add_parser('stat', aliases=['s'],
                                          help='Get stats.')
        stat_parser.set_defaults(func=self.stat)

        args = parser.parse_args()

        if args.verbose:
            logger.setLevel(logging.DEBUG)

        self.args = args

        if args.func is None:
            parser.print_help()
            sys.exit(0)

    def cmd_entry_point(self):
        '''Entry point for command line interaction'''
        # Create directories if missing
        self.create_dirs()

        args = self.args

        # Setup the directories
        self.create_dirs()

        # Call selected function
        args.func(args)


if __name__ == '__main__':
    clh = CmdLineHandler()
    clh.cmd_entry_point()

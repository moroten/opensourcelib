import datetime
import unittest
from textwrap import dedent
from unittest.mock import Mock, patch

from znake.builddir import BuildDir
from znake.venv import _render_write_pip_config_command, \
    _render_write_requirements_dev_file_command, _render_write_requirements_file_command, \
    _render_write_version_file_command, get_namespace


class TestRender(unittest.TestCase):

    def test_render_write_version_file_command(self):
        ctx = self._get_mock_config()
        ctx.znake.info.package = 'my_python_package'
        ctx.znake.info.changelog = [
            {
                'version': '2.0.0',
                'changes': [
                    'bug fixes and performance improvements',
                ],
                'date': 'tuesday'
            }, {
                'version': '1.0.0',
                'changes': [
                    'bug fixes',
                    'performance improvements',
                    "line with a ' quote in it",
                ],
                'date': 'thursday'
            }
        ]
        ctx.znake.deb.package = 'my_debian_package'
        ctx.znake.info.short_description = 'this is my short description'
        ctx.znake.info.long_description = dedent(
            """\
            this is
            my long description
            """)
        ctx.znake.info.maintainer = 'groovystacktraceguy52'
        ctx.znake.info.maintainer_email = 'groovystacktraceguy52@email.com'

        datetime_mock = Mock()
        datetime_mock.now.return_value = datetime.datetime(2018, 1, 2)
        with patch('os.getenv', return_value=23),\
                patch('datetime.datetime', new=datetime_mock):
            result = _render_write_version_file_command(ctx)
            self.assertEqual(
                result,
                dedent(
                    """\
                    # This file is automatically generated by Znake
                    from textwrap import dedent

                    __version__ = '2.0.0+23'
                    __updated__ = '2018-01-02'
                    deb_package_name = 'my_debian_package'
                    description = 'this is my short description'
                    long_description = dedent('''\\\\
                        this is
                        my long description
                        ''')
                    maintainer = 'groovystacktraceguy52'
                    maintainer_email = 'groovystacktraceguy52@email.com'

                    changelog = [
                        {
                            'version': '2.0.0',
                            'date': 'tuesday',
                            'changes': [
                                '''bug fixes and performance improvements''',
                            ],
                        },
                        {
                            'version': '1.0.0',
                            'date': 'thursday',
                            'changes': [
                                '''bug fixes''',
                                '''performance improvements''',
                                '''line with a ' quote in it''',
                            ],
                        },
                    ]
                    """))

    def test_render_write_pip_config_command(self):
        result = _render_write_pip_config_command()
        self.assertEqual(
            result,
            dedent(
                """\
                cat <<EOF>.venv/pip.conf
                [global]
                index-url = http://pip.zenterio.lan/simple
                extra-index-url = https://pypi.org/simple

                [install]
                trusted-host = pip.zenterio.lan
                EOF
                """))

    def test_render_write_requirements_file_command(self):
        ctx = self._get_mock_config()
        ctx.znake.requirements = [
            'a==1',
            'b==2',
            'c==3',
        ]
        result = _render_write_requirements_file_command(ctx)
        self.assertEqual(
            result,
            dedent(
                """\
                mkdir -p ./build/requirements && cat <<EOF>./build/requirements/requirements.txt
                --trusted-host pip.zenterio.lan
                a==1
                b==2
                c==3
                EOF
                """))

    def test_render_write_requirements_dev_file_command(self):
        ctx = self._get_mock_config()
        ctx.znake.requirements_dev = [
            'a==1',
            'b==2',
            'c==3',
        ]
        result = _render_write_requirements_dev_file_command(ctx)
        self.assertEqual(
            result,
            dedent(
                """\
                mkdir -p ./build/requirements && cat <<EOF>./build/requirements/requirements-dev.txt
                --trusted-host pip.zenterio.lan
                a==1
                b==2
                c==3
                EOF
                """))

    def _get_mock_config(self):
        config = Mock()
        config.build_dir = BuildDir()
        return config


class TestGetNamespace(unittest.TestCase):

    def test_get_namespace_with_no_targets(self):
        config = self._get_mock_config()
        namespace = get_namespace(config)
        assert len(namespace.tasks) == 2
        assert len(namespace.collections) == 0

    def _get_mock_config(self):
        config = Mock()
        config.build_dir = BuildDir()
        config.znake.test.targets = []
        config.znake.systest.targets = []
        return config

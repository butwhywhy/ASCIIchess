from setuptools import setup, find_packages

setup(
        name='ASCIIchess',
        version='0.1.0.dev',
        description='Minimal chess engine with basic command line, ASCI-art like, user interface',
        url='https://github.com/butwhywhy/ASCIIchess',
        author='Guillermo Horcajada Reales',
        author_email='guillerhr@gmail.com',

        license='MIT',

        packages=['ascii_drawing', 'ascii_chess'],
        package_data={'ascii_chess': ['ascii_chess_pieces/*',]
            },

        entry_points={
            'console_scripts': [
                'chess_cli = ascii_chess.chess_cli:play',
                ]
            },
        )


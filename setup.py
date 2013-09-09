from setuptools import setup

setup(name='zjujwbtools',
      version='0.1',
      description='A simple application to dump icalendar file from jwbinfosys.zju.edu.cn',
      author=['Dongyuan LIU', 'Pengyu CHEN'],
      author_email=['liu.dongyuan@gmail.com', 'cpy.prefers.you@gmail.com'],
      url='', # TBD
      install_requires=['requests', 'beautifulsoup4', 'PyYAML', 'icalendar', 'bottle'],
     )

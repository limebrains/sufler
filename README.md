# Sufler
 
Sufler - is the tool to help you with generating bash/zsh/powershell/fish autocompletions from YAML file. 

[![Build Status](https://travis-ci.org/limebrains/sufler.svg?branch=master)](https://travis-ci.org/limebrains/sufler)
[![coveralls](https://coveralls.io/repos/limebrains/sufler/badge.svg?branch=master&service=github)](https://coveralls.io/github/limebrains/sufler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/sufler/badge/?version=latest)](http://sufler.readthedocs.io/en/latest/?badge=latest)

[Documentation](http://sufler.readthedocs.io/en/latest/?badge=latest)
 
## Usage

[![gif](https://i.imgur.com/u09q5be.gif)](http://sufler.readthedocs.io)

```bash
| => sufler --help
Usage: sufler [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  init     initialize Sufler directory and config file
  install  install completions
  run      run command from <Run >

```
 
## Quickstart:

```bash
pip install sufler
```

or 

```
bash -c "$(curl -fsSL https://raw.githubusercontent.com/limebrains/sufler/master/install.bash)"
```

you will have directory in your home dir where you can install your custom completions.
```
/Users/pythonicninja/.sufler/
├── completions
│   ├── npm.yml
│   └── pip.yml
└── .config
```

there is repo which accepts PR's with common completions 
[sufler-completions - github.com](https://github.com/limebrains/sufler-completions)

## Key ideas:

### Example yml file:
```yaml
'pip': &pip
    'install': &install
        '--constrain': &constraint
            '<File>': *install
        '--build': &build
            '<File>': *install
        '--no-deps': *install
        '--install-option':
          '<Exec> wget https://pypi.python.org/simple/ -O ~/.sufler/python_completions -c -q && cat ~/.sufler/python_completions | cut -d ">" -f 2 | cut -d "<" -f 1 | grep "^TREE~1.*"': *install
```
[full raw file](https://raw.githubusercontent.com/limebrains/sufler-completions/master/completions/pip.yml)

Please notice special names of keys such as:

- `<Exec>`

- `<File>`

- `<Regex>`

- `<Run>`

[All of them are documented in details - readthedocs.io](http://sufler.readthedocs.io/en/latest/user/advanced.html)

### Origin of the name
Name comes from (pol. sufler - [wiki](https://pl.wikipedia.org/wiki/Sufler))  
> The prompter (sometimes prompt) in a theatre is a person who prompts or cues actors when they forget their lines or neglect to move on the stage to where they are supposed to be situated. 
 
![sufler](https://i.imgur.com/MWrtIhi.jpg)

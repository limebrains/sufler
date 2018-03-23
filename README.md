# Sufler
 
Sufler - is the tool to help you with generating bash/zsh/powershell/fish autocompletions from yml file. 

[![travis](https://img.shields.io/travis/limebrains/sufler.svg)](https://travis-ci.org/limebrains/sufler)
[![coveralls](https://coveralls.io/repos/limebrains/sufler/badge.svg?branch=master&service=github)](https://coveralls.io/github/limebrains/sufler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/sufler/badge/?version=latest)](http://sufler.readthedocs.io/en/latest/?badge=latest)

[Documentation](http://sufler.readthedocs.io/en/latest/?badge=latest)
 
## Quickstart:
```
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/limebrains/sufler/master/install.bash)"
```

or

```bash
pip install sufler
```

you will have directory in your home dir where you can install your custom completions.
```
/Users/pythonicninja/.sufler/
├── completions
│   ├── npm.yml
│   └── pip.yml
└── .config
```

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

Please notice special names of keys such as:

- `<Exec>`

- `<File>`

- `<Regex>`

- `<Run>`

All of them are documented in details - [http://sufler.readthedocs.io/en/latest/user/advanced.html](documentation of advanced features)

### Origin of the name
Name comes from (pol. sufler - [https://pl.wikipedia.org/wiki/Sufler](sufler))  
> The prompter (sometimes prompt) in a theatre is a person who prompts or cues actors when they forget their lines or neglect to move on the stage to where they are supposed to be situated. 
 
![sufler](https://i.imgur.com/MWrtIhi.jpg)

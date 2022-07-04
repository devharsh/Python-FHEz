# Python-FHEz
This repository is an upgraded version of https://github.com/DreamingRaven/python-fhez compatible with Python 3 and Microsoft SEAL 4.


# How to run

Follow the build instructions for Microsoft SEAL Python bindings from https://github.com/Huelse/SEAL-Python#build before building this project! You may place your shared library (```.so``` for Linux* or ```.dll``` for Windows) in examples directory.

- ```$git clone https://github.com/devharsh/Python-FHEz```
- ```$cd Python-FHEz```
- ```$python3 setup.py build```
- ```$python3 setup.py install```
- ```$cd examples```
- ```$jupyter lab```


# Cite

## Original Version

Either:
```
@online{reseal,
  author = {George Onoufriou},
  title = {Python-FHEz Source Repository},
  howpublished = {GitLab},
  year = {2021},
  url = {https://gitlab.com/DeepCypher/python-fhez},
}
```

Or if you do not have @online support:
```
@misc{reseal,
  author = {George Onoufriou},
  title = {Python-FHEz Source Repository},
  howpublished = {GitLab},
  year = {2021},
  note = {\url{https://gitlab.com/DeepCypher/python-fhez}},
}
```

## This Repository

Either:
```
@online{reseal4dev,
  author = {Devharsh Trivedi},
  title = {Python-FHEz SEAL4 Source Repository},
  howpublished = {GitHub},
  year = {2022},
  url = {https://github.com/devharsh/Python-FHEz},
}
```

Or if you do not have @online support:
```
@misc{reseal4dev,
  author = {George Onoufriou},
  title = {Python-FHEz SEAL4 Source Repository},
  howpublished = {GitHub},
  year = {2022},
  note = {\url{https://github.com/devharsh/Python-FHEz}},
}
```

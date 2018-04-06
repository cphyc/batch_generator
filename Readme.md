# Batch generator

This utility helps creating and submitting jobs on clusters. It also provides a unified interface to some popular job schedular (qsub and slurm).

## Install

```bash
git clone <>
pip install .
```

## Usage

To get a rough idea of how to use the utility, use
```
batch --help
```
or send me an email.

## Templates

The utility helps creating jobs using templates. Template are bash files with placeholders: the utility helps to fill the placeholders for you!
Templates should be stored in `~/.local/share/batch_generator/` on Linux systems and be valid bash files.

Placeholders have the following syntax:
```
{{name:type|Description}}
{{name:type|Description|default value}}
{{valid python code}}
```
The type should be a valid python type (e.g. `int`, `str`, `float`).

### Note about expressions
In the last case, the expression will be evaluated by Python providing the previously entered values.

### Example
Here is a (very) simple template for the qsub system:
```
#PBS -l nodes={{nodes:int|Number of nodes|1}}:ppn={{ppn:int|Number of process per node|16}}

echo Running on {{nodes*ppn}}.
```
If you run `batch`:
```
$ batch g
Number of nodes [1]: 2
Number of process per node [16]: 32
$ cat job.sh
#PBS -l nodes=2:ppn=32

echo Running on 64 nodes.
```

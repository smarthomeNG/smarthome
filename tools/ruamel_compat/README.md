# ruamel_compat

Checks what a ruamel.yaml version does to SmartHomeNG's YAML files, before the pin in
`lib/requirements.txt` is moved.

Every YAML file of the corpus goes through two pipelines:

- `shng`: `lib/shyaml.py` as it is in this tree - `yaml_load()` (with and without ordering) and the round
  trip `yaml_load_roundtrip()` -> `yaml_dump_roundtrip()` that the admin interface and
  `Items.create_item()` use to edit configuration files.
- `plain`: ruamel.yaml's own round trip (`YAML(typ='rt')`, 4 space indentation, quotes preserved), as a
  reference for what ruamel.yaml itself keeps.

Per file and pipeline a run records the loaded data (type-exact), the logged warnings and errors, the file
after saving it unchanged and after one edit, whether the saved file reads back to the same data, lost
comments and changed lines. A token table shows how values like `yes`, `1:20`, `010` or `0049123456` are
read, saved and read again.

## Usage

```
# both versions in venvs of their own, with the plugins' metadata as additional corpus
tools/ruamel_compat/ruamel_compat.py matrix 0.16.7 0.19.1 --corpus plugins --corpus etc

# or step by step, each run with the interpreter that has the ruamel.yaml version to test
python tools/ruamel_compat/ruamel_compat.py run --out old.json --corpus etc
python tools/ruamel_compat/ruamel_compat.py run --out new.json --corpus etc
python tools/ruamel_compat/ruamel_compat.py compare old.json new.json
```

`matrix` installs each version with pip into `<workdir>/ruamel-<version>` (default: below the system temp
directory; reused on the next call) and needs network access for that. Only `.yaml` files are read;
`_pv_*` and `priv_*` directories are skipped. A real configuration (a copy of `etc/` with items, structs
and scenes) is the most telling corpus; the result files contain the data and texts of the files, so keep
them private.

## Reading the report

For each pipeline the report lists, data first:

| entry | meaning |
|---|---|
| `safe`, `safe_ordered` | data read by `yaml_load()` (plain: the safe loader) |
| `data` | data read by the round trip loader |
| `reload_same` | the saved file reads back to the same data |
| `log` | warnings and errors logged by `lib.shyaml` (duplicate keys, parse errors) |
| `saved`, `edited` | the file text after saving it unchanged / after one edit |

with the first differing place of up to five files, then the fidelity sums (files that fail to load or
save, lines changed, comments lost, files that read back different) and the tokens that behave
differently. `UNUSABLE` means the pipeline fails on every file with that version - for `shng` the API
`lib/shyaml.py` uses is not available.

## Corpus

`corpus/` holds small files for the cases that matter for SmartHomeNG: YAML 1.1 vs 1.2 values
(`tokens_*`), comments in every position (also between `%YAML` and `---`), block scalars, anchors and merge
keys, flow style, duplicate keys, special characters, struct and eval syntax, plugin metadata, CRLF, BOM,
empty files and broken files (`err_*`). `corpus/.gitattributes` keeps them byte-exact.

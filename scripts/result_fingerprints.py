"""Normalized SHA-256 checks for compact, recorded experiment results."""
import csv
import hashlib
import json

TIMING = {'seconds', 'processing_seconds', 'clustering_seconds'}


def without_timing(value):
    if isinstance(value, dict):
        return {k: without_timing(v) for k, v in value.items() if k not in TIMING}
    if isinstance(value, list):
        return [without_timing(v) for v in value]
    return value


def fingerprint(path, kind):
    if kind == 'csv':
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.reader(stream)
            columns = next(reader)
            selected = [i for i, name in enumerate(columns) if name not in TIMING]
            rows = []
            for row in reader:
                if len(row) != len(columns):
                    raise ValueError('CSV 列数不一致：' + str(path))
                rows.append([row[i] for i in selected])
            value = {'columns': [columns[i] for i in selected], 'rows': rows}
    elif kind == 'json':
        value = without_timing(json.loads(path.read_text(encoding='utf-8')))
    else:
        raise ValueError('未知指纹类型：' + kind)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def build_fingerprints(folder, csvs, jsons):
    return {'schema_version': 1, 'ignored_fields': sorted(TIMING), 'files': {
        name: {'kind': kind, 'sha256': fingerprint(folder / name, kind)}
        for kind, names in (('csv', csvs), ('json', jsons)) for name in names
    }}


def verify_fingerprints(generated, evidence, csvs, jsons):
    if evidence.get('schema_version') != 1 or evidence.get('ignored_fields') != sorted(TIMING):
        raise ValueError('不支持的结果指纹格式')
    expected = {name: kind for kind, names in (('csv', csvs), ('json', jsons)) for name in names}
    entries = evidence.get('files', {})
    if not isinstance(entries, dict) or set(entries) != set(expected):
        raise ValueError('结果指纹清单必须完整覆盖规定的 26 CSV 和 8 JSON')
    for name, kind in expected.items():
        entry = entries[name]
        if not isinstance(entry, dict) or entry.get('kind') != kind:
            raise ValueError('结果指纹格式错误：' + name)
        path = generated / name
        if not path.is_file():
            raise FileNotFoundError('缺少最终结果：' + name)
        if fingerprint(path, kind) != entry.get('sha256'):
            raise AssertionError('最终结果与原始运行指纹不一致：' + name)
    return {'csv': list(csvs), 'json': list(jsons)}

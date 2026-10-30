"""Compact evidence must verify every required result, including lost files."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import replay


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


class CompactResultsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.generated = Path(self.temp.name) / 'generated'
        self.recorded = Path(self.temp.name) / 'recorded'
        self.recorded.mkdir()
        self.payload = {'schema_version': 1, 'ignored_fields': sorted(replay.TIMING), 'files': {}}
        for name in replay.FINAL_CSVS:
            path = self.generated / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('source_row_id,value,seconds\n1,2,99\n', encoding='utf-8-sig')
            self.payload['files'][name] = {'kind': 'csv', 'sha256': sha({'columns': ['source_row_id', 'value'], 'rows': [['1', '2']]})}
        for name in replay.FINAL_JSONS:
            path = self.generated / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"rows":1,"processing_seconds":99}', encoding='utf-8')
            self.payload['files'][name] = {'kind': 'json', 'sha256': sha({'rows': 1})}
        self.save()

    def save(self):
        (self.recorded / 'result_fingerprints.json').write_text(json.dumps(self.payload), encoding='utf-8')

    def test_full_set_matches_without_duplicate_result_tables(self):
        checked = replay.verify_final_results(self.generated, self.recorded)
        self.assertEqual(checked, {'csv': list(replay.FINAL_CSVS), 'json': list(replay.FINAL_JSONS)})

    def test_changed_cluster_value_rejected(self):
        (self.generated / 'agent/clusters.csv').write_text('source_row_id,value,seconds\n1,9,99\n', encoding='utf-8')
        with self.assertRaisesRegex(AssertionError, 'agent/clusters.csv'):
            replay.verify_final_results(self.generated, self.recorded)

    def test_missing_fingerprint_rejected(self):
        del self.payload['files']['agent/clusters.csv']
        self.save()
        with self.assertRaisesRegex(ValueError, '指纹清单'):
            replay.verify_final_results(self.generated, self.recorded)

    def test_missing_generated_file_rejected(self):
        (self.generated / 'agent/clusters.csv').unlink()
        with self.assertRaisesRegex(FileNotFoundError, 'agent/clusters.csv'):
            replay.verify_final_results(self.generated, self.recorded)

    def test_changed_json_rejected(self):
        (self.generated / 'agent/quality_after.json').write_text('{"rows":2}', encoding='utf-8')
        with self.assertRaisesRegex(AssertionError, 'agent/quality_after.json'):
            replay.verify_final_results(self.generated, self.recorded)

    def test_unknown_schema_rejected(self):
        self.payload['schema_version'] = 999
        self.save()
        with self.assertRaisesRegex(ValueError, '指纹格式'):
            replay.verify_final_results(self.generated, self.recorded)


if __name__ == '__main__':
    unittest.main()

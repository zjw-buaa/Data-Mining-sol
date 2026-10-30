"""Reconcile published supplementary summaries against the three real runs."""
import csv
import json
import math
from pathlib import Path
import statistics
import unittest

ROOT = Path(__file__).resolve().parents[1]
STABILITY = ROOT / 'results/stability'


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


class StabilityEvidenceTests(unittest.TestCase):
    def test_three_distinct_calls_match_recorded_policy_and_metrics(self):
        records = rows(STABILITY / 'runs.csv')
        self.assertEqual([int(row['original_run']) for row in records], [2, 3, 4])
        self.assertEqual(len({row['response_id'] for row in records}), 3)
        self.assertEqual(sum(int(row['total_tokens']) for row in records), 4077)
        for row in records:
            folder = STABILITY / 'runs' / f"{int(row['original_run']):02}"
            status = json.loads((folder / 'agent_status.json').read_text('utf-8'))
            selected = next(r for r in rows(folder / 'comparison.csv') if r['group'] == 'agent')
            self.assertTrue(status['real_model_called'])
            self.assertEqual(status['calls'], 1)
            policy = status['validated_plan']['policy']
            self.assertEqual(policy['deduplicate'], row['deduplicate'] == 'True')
            self.assertEqual(policy['rating'], row['rating'])
            self.assertEqual(policy['size'], row['size'])
            for field in ('cluster_rows', 'cluster_retention', 'silhouette', 'davies_bouldin', 'k', 'size_imputed'):
                self.assertEqual(float(row[field]), float(selected[field]))
            self.assertEqual(int(row['total_tokens']), status['prompt_tokens'] + status['completion_tokens'])
            events = [json.loads(line) for line in (folder / 'logs/pipeline.jsonl').read_text('utf-8').splitlines()]
            responses = [event['response']['id'] for event in events if event['event'] == 'llm_response']
            self.assertEqual(responses, [row['response_id']])

    def test_summary_uses_only_three_supplements_and_sample_standard_deviation(self):
        records = rows(STABILITY / 'runs.csv')
        for row in rows(STABILITY / 'metrics_summary.csv'):
            with self.subTest(metric=row['metric']):
                values = [float(record[row['metric']]) for record in records]
                self.assertEqual(int(row['n']), 3)
                expected = {'mean': statistics.mean(values), 'sample_variance': statistics.variance(values),
                            'sample_std': statistics.stdev(values), 'min': min(values), 'max': max(values)}
                for field, value in expected.items():
                    self.assertTrue(math.isclose(float(row[field]), value, rel_tol=1e-12, abs_tol=1e-12), (row['metric'], field))

    def test_completed_review_has_twelve_records(self):
        review = rows(ROOT / 'docs/review/records.csv')
        self.assertEqual(len(review), 12)
        self.assertEqual(len({row['source_row_id'] for row in review}), 12)
        self.assertEqual({row['人工是否合理'] for row in review}, {'合理'})


if __name__ == '__main__':
    unittest.main()

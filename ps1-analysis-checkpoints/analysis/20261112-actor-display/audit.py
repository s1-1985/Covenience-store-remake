#!/usr/bin/env python3
"""Connect natural staff positions to original actor image codes and records."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
reports = []
for case in ('first-store', 'second-store'):
    path = ROOT / (case + '-results.json')
    result = json.loads(path.read_text())
    assert result['all_passed'] and result.get('case', 'second-store') == case
    offsets = result['direction_image_offsets']
    assert offsets == [1, 0, 2, 3]
    matched = 0
    shifts = 0
    movements = []
    unmatched = 0
    resting = 0
    customer_matches = 0
    previous = {}
    for row in result['cases']:
        remaining = list(row['actors'])
        for person in row['personnel']:
            if person['state'] == 0:
                candidates = [a for a in remaining if a['source'] == 'resting_staff' and a['id'] == person['id']]
                assert len(candidates) == int(person['appended'])
                if candidates:
                    remaining.remove(candidates[0])
                    resting += 1
                continue
            image = 640 + 4 * person['appearance'] + offsets[person['direction']]
            candidates = [a for a in remaining if a['source'] == 'grid' and
                          a['cell'] == person['cell'] and a['image'] == image]
            assert len(candidates) == 1, (case, row['clock'], person, candidates)
            actor = candidates[0]
            remaining.remove(actor)
            matched += 1
            shifts += int(actor['right_fixture_shift'])
            key = person['id']
            last = previous.get(key)
            if last and last['cell'] != person['cell']:
                movements.append(dict(id=key, before_clock=last['clock'], clock=row['clock'],
                                      before_cell=last['cell'], cell=person['cell'],
                                      before_pixel=last['pixel'], pixel=actor['pixel'],
                                      image=image, direction=person['direction']))
            previous[key] = dict(clock=row['clock'], cell=person['cell'], pixel=actor['pixel'])
        for person in row.get('customers', []):
            image = 640 + 4 * person['appearance'] + offsets[person['direction']]
            candidates = [a for a in remaining if a['source'] == 'grid' and a['cell'] == person['cell'] and a['image'] == image]
            if candidates:
                assert len(candidates) == 1
                remaining.remove(candidates[0])
                customer_matches += 1
        unmatched += len(remaining)
    reports.append(dict(case=case, display_checks=len(result['cases']),
                        source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        actor_records=sum(row['count'] for row in result['cases']),
                        staff_records_matched=matched, right_fixture_shifts=shifts,
                        resting_staff_records_matched=resting, customer_records_matched=customer_matches,
                        nonstaff_grid_records=unmatched, observed_movements=movements,
                        state_counts=dict(collections.Counter(p['state'] for row in result['cases'] for p in row['personnel']))))
output = dict(all_passed=True, display_checks=sum(r['display_checks'] for r in reports),
              staff_records_matched=sum(r['staff_records_matched'] for r in reports),
              resting_staff_records_matched=sum(r['resting_staff_records_matched'] for r in reports),
              customer_records_matched=sum(r['customer_records_matched'] for r in reports),
              actor_records=sum(r['actor_records'] for r in reports), cases=reports,
              limits=['Nonstaff grid records are counted without inferring an identity from image alone.',
                      'Resting and customer coverage are counted only when matching collected natural state.',
                      'Movement observations are CPU records, not a measured GPU animation or real-time rate.'])
(ROOT / 'audit.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: output[k] for k in ('all_passed', 'display_checks', 'staff_records_matched', 'actor_records')}))

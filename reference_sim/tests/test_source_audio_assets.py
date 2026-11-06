"""Provenance and delivery checks for actual recovered audio, not synthesis mocks."""
from pathlib import Path
import hashlib, json, unittest

ROOT=Path(__file__).resolve().parents[2]

class SourceAudioAssetTests(unittest.TestCase):
    def test_every_delivered_audio_asset_matches_registered_original_conversion(self):
        data=json.loads((ROOT/'game/data/source_audio.json').read_text())
        folder=ROOT/'game/assets/audio/source'
        expected=set()
        for kind,count in [('xa',130),('bgm',7),('se',16),('vos',12)]:
            self.assertEqual(len(data[kind]),count)
            for index,entry in enumerate(data[kind]):
                self.assertEqual(entry['id'],index)
                path=folder/entry['file'];expected.add(path)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),entry['sha256'])
                self.assertEqual(path.read_bytes()[:4],b'OggS')
                self.assertGreater(entry['duration'],0)
        self.assertEqual(set(folder.glob('*.ogg')),expected)
        self.assertEqual(data['excluded_row130'],[3000000,7000000,10000000])
        for row in data['xa']:
            self.assertEqual(row['frames'],row['sector_units']*4032//row['channels'])
            self.assertEqual(row['dispatcher_id'],row['id']+28)
        self.assertEqual(data['bgm_settings'],[-1,2,3,4])
        self.assertIn('REMAKE_BALANCED_DEFAULT',data['sequence_evidence_note'])

    def test_runtime_cannot_require_original_disc_or_offline_synthesizer(self):
        text=(ROOT/'game/scripts/audio/sound_manager.gd').read_text()
        for runtime_dependency in ['Unicorn','tinysoundfont','SLPS_007','SOUND.XA','sfload(']:
            self.assertNotIn(runtime_dependency,text)
        for module in ['module_ogg_enabled=yes','module_vorbis_enabled=yes']:
            self.assertIn(module,(ROOT/'tools/build_godot_templates.sh').read_text())

if __name__=='__main__':unittest.main()

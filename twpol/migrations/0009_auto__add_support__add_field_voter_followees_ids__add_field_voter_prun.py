# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Support'
        db.create_table(u'twpol_support', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['twpol.Candidate'])),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['twpol.Voter'])),
            ('when', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'twpol', ['Support'])

        # Adding field 'Voter.followees_ids'
        db.add_column(u'twpol_voter', 'followees_ids',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Voter.pruned_followees_ids'
        db.add_column(u'twpol_voter', 'pruned_followees_ids',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Voter.downloaded_followees'
        db.add_column(u'twpol_voter', 'downloaded_followees',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding M2M table for field followees on 'Voter'
        db.create_table(u'twpol_voter_followees', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_voter', models.ForeignKey(orm[u'twpol.voter'], null=False)),
            ('to_voter', models.ForeignKey(orm[u'twpol.voter'], null=False))
        ))
        db.create_unique(u'twpol_voter_followees', ['from_voter_id', 'to_voter_id'])


    def backwards(self, orm):
        # Deleting model 'Support'
        db.delete_table(u'twpol_support')

        # Deleting field 'Voter.followees_ids'
        db.delete_column(u'twpol_voter', 'followees_ids')

        # Deleting field 'Voter.pruned_followees_ids'
        db.delete_column(u'twpol_voter', 'pruned_followees_ids')

        # Deleting field 'Voter.downloaded_followees'
        db.delete_column(u'twpol_voter', 'downloaded_followees')

        # Removing M2M table for field followees on 'Voter'
        db.delete_table('twpol_voter_followees')


    models = {
        u'twpol.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'account_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True'}),
            'candidate_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'candidate_type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'candidate_primarily_lives_in'", 'null': 'True', 'to': u"orm['twpol.District']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'migrated_followers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'num_followers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'party_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'twitter_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        u'twpol.district': {
            'Meta': {'object_name': 'District'},
            'district_number': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state_code': ('django.db.models.fields.IntegerField', [], {})
        },
        u'twpol.support': {
            'Meta': {'object_name': 'Support'},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twpol.Candidate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twpol.Voter']"}),
            'when': ('django.db.models.fields.DateField', [], {})
        },
        u'twpol.voter': {
            'Meta': {'object_name': 'Voter'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voter_primarily_lives_in'", 'null': 'True', 'to': u"orm['twpol.District']"}),
            'downloaded_followees': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'downloaded_followers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'error_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3'}),
            'followees': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followees_rel_+'", 'to': u"orm['twpol.Voter']"}),
            'followees_ids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followers_rel_+'", 'to': u"orm['twpol.Voter']"}),
            'followers_ids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'num_followers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'over_max_followers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'party_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'pruned_followees_ids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pruned_followers_ids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'supports': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['twpol.Candidate']", 'symmetrical': 'False'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['twpol']
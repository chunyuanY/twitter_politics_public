# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Voter.account_no_exists'
        db.delete_column(u'twpol_voter', 'account_no_exists')

        # Adding field 'Voter.error_code'
        db.add_column(u'twpol_voter', 'error_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=3),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Voter.account_no_exists'
        db.add_column(u'twpol_voter', 'account_no_exists',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Voter.error_code'
        db.delete_column(u'twpol_voter', 'error_code')


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
        u'twpol.voter': {
            'Meta': {'object_name': 'Voter'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voter_primarily_lives_in'", 'null': 'True', 'to': u"orm['twpol.District']"}),
            'downloaded_followers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'error_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followers_rel_+'", 'to': u"orm['twpol.Voter']"}),
            'followers_ids': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'num_followers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'over_max_followers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'party_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'pruned_followers_ids': ('django.db.models.fields.TextField', [], {}),
            'supports': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['twpol.Candidate']", 'symmetrical': 'False'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['twpol']
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'District'
        db.create_table(u'twpol_district', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('district_number', self.gf('django.db.models.fields.IntegerField')()),
            ('state_code', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'twpol', ['District'])

        # Adding model 'Candidate'
        db.create_table(u'twpol_candidate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('twitter_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('twitter_screen_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(related_name='candidate_primarily_lives_in', null=True, to=orm['twpol.District'])),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('party_num', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('twitter_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('candidate_type', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('candidate_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('account_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('candidate_id', self.gf('django.db.models.fields.CharField')(max_length=9, null=True)),
        ))
        db.send_create_signal(u'twpol', ['Candidate'])

        # Adding model 'Voter'
        db.create_table(u'twpol_voter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('twitter_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('twitter_screen_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(related_name='voter_primarily_lives_in', null=True, to=orm['twpol.District'])),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('party_num', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('invalid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('num_followers', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'twpol', ['Voter'])

        # Adding M2M table for field supports on 'Voter'
        db.create_table(u'twpol_voter_supports', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('voter', models.ForeignKey(orm[u'twpol.voter'], null=False)),
            ('candidate', models.ForeignKey(orm[u'twpol.candidate'], null=False))
        ))
        db.create_unique(u'twpol_voter_supports', ['voter_id', 'candidate_id'])

        # Adding M2M table for field followers on 'Voter'
        db.create_table(u'twpol_voter_followers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_voter', models.ForeignKey(orm[u'twpol.voter'], null=False)),
            ('to_voter', models.ForeignKey(orm[u'twpol.voter'], null=False))
        ))
        db.create_unique(u'twpol_voter_followers', ['from_voter_id', 'to_voter_id'])


    def backwards(self, orm):
        # Deleting model 'District'
        db.delete_table(u'twpol_district')

        # Deleting model 'Candidate'
        db.delete_table(u'twpol_candidate')

        # Deleting model 'Voter'
        db.delete_table(u'twpol_voter')

        # Removing M2M table for field supports on 'Voter'
        db.delete_table('twpol_voter_supports')

        # Removing M2M table for field followers on 'Voter'
        db.delete_table('twpol_voter_followers')


    models = {
        u'twpol.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'account_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True'}),
            'candidate_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'candidate_type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'candidate_primarily_lives_in'", 'null': 'True', 'to': u"orm['twpol.District']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
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
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followers_rel_+'", 'to': u"orm['twpol.Voter']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'num_followers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'party_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'supports': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['twpol.Candidate']", 'symmetrical': 'False'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['twpol']
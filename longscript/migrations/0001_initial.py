# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScriptException'
        db.create_table(u'longscript_scriptexception', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exception_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('item_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal(u'longscript', ['ScriptException'])

        # Adding model 'Script'
        db.create_table(u'longscript_script', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('running', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('num_total_items', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('num_processed_items', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('num_exceptions', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('num_successes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bonus_data', self.gf('django.db.models.fields.TextField')()),
            ('time_distribution', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'longscript', ['Script'])

        # Adding M2M table for field exceptions on 'Script'
        db.create_table(u'longscript_script_exceptions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('script', models.ForeignKey(orm[u'longscript.script'], null=False)),
            ('scriptexception', models.ForeignKey(orm[u'longscript.scriptexception'], null=False))
        ))
        db.create_unique(u'longscript_script_exceptions', ['script_id', 'scriptexception_id'])


    def backwards(self, orm):
        # Deleting model 'ScriptException'
        db.delete_table(u'longscript_scriptexception')

        # Deleting model 'Script'
        db.delete_table(u'longscript_script')

        # Removing M2M table for field exceptions on 'Script'
        db.delete_table('longscript_script_exceptions')


    models = {
        u'longscript.script': {
            'Meta': {'object_name': 'Script'},
            'bonus_data': ('django.db.models.fields.TextField', [], {}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'exceptions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['longscript.ScriptException']", 'symmetrical': 'False'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'num_exceptions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_processed_items': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_successes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_total_items': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'running': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'time_distribution': ('django.db.models.fields.TextField', [], {})
        },
        u'longscript.scriptexception': {
            'Meta': {'object_name': 'ScriptException'},
            'exception_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['longscript']
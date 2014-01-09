# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScriptSpecialError'
        db.create_table(u'longscript_scriptspecialerror', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('which_error', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('num_errors', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'longscript', ['ScriptSpecialError'])


    def backwards(self, orm):
        # Deleting model 'ScriptSpecialError'
        db.delete_table(u'longscript_scriptspecialerror')


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
            'exception_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'longscript.scriptsleep': {
            'Meta': {'object_name': 'ScriptSleep'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seconds_slept': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'longscript.scriptspecialerror': {
            'Meta': {'object_name': 'ScriptSpecialError'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_errors': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'which_error': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['longscript']
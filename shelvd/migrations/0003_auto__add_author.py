# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Author'
        db.create_table(u'shelvd_author', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('nationality', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('ethnicity', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
        ))
        db.send_create_signal(u'shelvd', ['Author'])


    def backwards(self, orm):
        # Deleting model 'Author'
        db.delete_table(u'shelvd_author')


    models = {
        u'shelvd.author': {
            'Meta': {'object_name': 'Author'},
            'ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'nationality': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'})
        },
        u'shelvd.book': {
            'Meta': {'object_name': 'Book'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '13', 'primary_key': 'True'}),
            'last_action_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'page_count': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'shelvd.bookmark': {
            'Meta': {'object_name': 'Bookmark'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pages_read': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reading': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookmarks'", 'to': u"orm['shelvd.Reading']"})
        },
        u'shelvd.reading': {
            'Meta': {'object_name': 'Reading'},
            'abandoned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'readings'", 'to': u"orm['shelvd.Book']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['shelvd']
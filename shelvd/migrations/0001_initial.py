# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Book'
        db.create_table(u'shelvd_book', (
            ('isbn', self.gf('django.db.models.fields.CharField')(max_length=13, primary_key=True)),
            ('nick', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('page_count', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('last_action_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'shelvd', ['Book'])

        # Adding model 'Reading'
        db.create_table(u'shelvd_reading', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='readings', to=orm['shelvd.Book'])),
            ('book_isbn', self.gf('django.db.models.fields.CharField')(max_length=13)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ended', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('abandoned', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'shelvd', ['Reading'])

        # Adding model 'Bookmark'
        db.create_table(u'shelvd_bookmark', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reading', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bookmarks', to=orm['shelvd.Reading'])),
            ('page', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('pages_read', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'shelvd', ['Bookmark'])


    def backwards(self, orm):
        # Deleting model 'Book'
        db.delete_table(u'shelvd_book')

        # Deleting model 'Reading'
        db.delete_table(u'shelvd_reading')

        # Deleting model 'Bookmark'
        db.delete_table(u'shelvd_bookmark')


    models = {
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
            'book_isbn': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['shelvd']
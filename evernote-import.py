from datetime import datetime
from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note
import sqlite3

dev_token = ':'.join([
    '<put token pieces here>'
])

moods = {
    1:    '691949b6-526d-464c-8f79-38097bdecfdf',
    .25:  'cefc2129-bb70-497e-9d74-ba9405671a73',
    .75:  'a59d4b1f-ea39-46a9-961c-826af01392e7',
    1.25: 'fb8f3772-3d19-4f94-860d-4529603a48cd',
    1.75: '1ca17b5f-8194-4070-8906-5b915a29b2df',
}


def get_journey_notes():
    conn = sqlite3.connect('Journey.db')
    c = conn.cursor()
    res = c.execute('select Text, Sentiment, DateOfJournal from Journal')
    return [{
        'text': r[0],
        'mood': r[1],
        'date': r[2],
    } for r in res]


def make_note(
        auth_token,
        note_store,
        title,
        body,
        date,
        tag,
        parent_notebook=None):

    # Create note object
    note = Note()
    note.title = title
    note.tagGuids = [tag]
    note.created = date
    note.updated = date
    note.content = ''.join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">',
        '<en-note>{}</en-note>'.format(body),
    ])

    # parent_notebook is optional; if omitted, default notebook is used
    if parent_notebook:
        note.notebookGuid = parent_notebook

    # Attempt to create note in Evernote account
    try:
        return note_store.createNote(note)
    except Exception as e:
        # Something was wrong with the note data
        # See EDAMErrorCode enumeration for error code explanation
        # http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        print('whoa', e)
        return None


if __name__ == '__main__':
    client = EvernoteClient(token=dev_token, sandbox=False)
    note_store = client.get_note_store()
    journal_guid = '66ecfcf2-37b9-4091-8679-722fcaf6985b'
    times = 0
    for entry in get_journey_notes():
        try:
            date_str = datetime.utcfromtimestamp(
                entry['date'] / 1000
            ).strftime('%B %d, %Y')
            make_note(
                dev_token,
                note_store,
                date_str,
                entry['text'],
                entry['date'],
                moods[entry['mood']],
                journal_guid,
            )
            print(date_str)
        except Exception as e:
            print('failed:', entry)
            print(e)
            print('')

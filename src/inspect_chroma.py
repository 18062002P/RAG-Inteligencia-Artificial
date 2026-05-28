from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class SimpleEmb:
    def embed_documents(self, texts):
        return [[0.0] for _ in texts]

    def embed_query(self, text):
        return [0.0]

# tiny doc
docs = [Document(page_content='hola', metadata={'source':'a'})]

store = Chroma.from_documents(docs, embedding=SimpleEmb(), persist_directory='./data/inspect_chroma', collection_name='test')
print('Chroma type:', type(store))
print('Attrs:', [a for a in dir(store) if not a.startswith('_')])
client = getattr(store, '_client', None)
print('Client:', type(client), repr(client))
if client is not None:
    print('Client attrs:', [a for a in dir(client) if not a.startswith('_')])
    try:
        db = getattr(client, 'database', None)
        print('Client.database:', type(db), repr(db))
        if db is not None:
            print('database attrs:', [a for a in dir(db) if not a.startswith('_')])
    except Exception as e:
        print('error inspecting database attr', e)

# try to persist and close
try:
    p = getattr(store, 'persist', None)
    print('persist callable?', callable(p))
    if callable(p):
        p()
except Exception as e:
    print('persist err', e)

try:
    if client is not None:
        for name in ('close','shutdown','stop','_shutdown'):
            fn = getattr(client, name, None)
            if callable(fn):
                print('calling client.', name)
                try:
                    fn()
                except Exception as e:
                    print('error calling', name, e)
except Exception as e:
    print('client close err', e)

print('done')

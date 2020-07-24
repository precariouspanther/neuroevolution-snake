import pickle


class SaveState(object):
    def __init__(self, path):
        self.path = path

    def save(self, data):
        with open(self.path, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def open(self):
        with open(self.path, 'rb') as handle:
            b = pickle.load(handle)
        return b

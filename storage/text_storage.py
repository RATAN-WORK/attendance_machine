
class File_IO:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def file_writer(self, data, path, mode)  :## mode == 'a' or 'w'
        with open(path, mode) as writer:
            writer.write(data)

    def file_reader(self, path):
        with open(path, 'r') as reader:
            data = reader.read()
            return data


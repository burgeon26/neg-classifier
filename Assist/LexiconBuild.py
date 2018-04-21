from Tool import read_from_file, write_to_file


def repeat_filter(path, new_path):
    """
    个性化词库去重工具
    :param path:
    :param new_path:
    """
    words = read_from_file(path)
    words = map(lambda x: x.replace('\n', ''), set(words))
    write_to_file(new_path, words)


if __name__ == '__main__':
    repeat_filter('/home/zhenlingcn/Desktop/ltp_data/word.txt', '/home/zhenlingcn/Desktop/ltp_data/new.txt')

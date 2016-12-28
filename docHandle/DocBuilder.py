#!/usr/bin/env python3
import jieba
import re

class DocBuilder(object):

    def __init__(self):
        self.document = []
        self.docs_index = []
        self.word_vector = {}
        self.word_count = 0
        self.inverse_word_index = []
        # number of documents
        self.M = 0

        # 读入停词表，目前停词表中还没有词，只有标点
        self.read_stopwords('data/stop_words.txt')

    def readDoc(self, path):
        with open(path, 'r', encoding='utf-8') as docs:
            for eachLine in docs:
                self.document.append(self.seg(eachLine.strip()))
                self.M += 1


    # read stop_words list from file
    def read_stopwords(self, path):
        self.stop_words = set()

        with open(path, 'r', encoding='utf-8') as stop_words_file:
            for eachLine in stop_words_file:
                self.stop_words.add(eachLine.strip())

    def seg(self, doc):
        result = []
        for word in jieba.cut(doc):
            new_word = self.filter(word)
            if new_word not in self.stop_words:
                result.append(new_word)

        return result


    def filter(self, input):
            line = input.strip()    #处理前进行相关的处理，包括转换成Unicode等
            p2 = re.compile('[^\u4e00-\u9fa5]')    #中文的编码范围是：\u4e00到\u9fa5
            # 数字和字母似乎都没用，所以我只留了汉字
            zh = "".join(p2.split(line)).strip()
            return zh

    def convert_to_vector(self):
        for doc in self.document:
            doc_index = []
            for word in doc:
                if word not in self.word_vector:
                    self.word_vector[word] = self.word_count
                    self.word_count += 1
                    self.inverse_word_index.append(word)
                doc_index.append(self.word_vector[word])
            self.docs_index.append(doc_index)

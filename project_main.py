import re
import string

import jieba
import pdfplumber
from snownlp import SnowNLP
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx
from textrank4zh import TextRank4Sentence, TextRank4Keyword
from openai import OpenAI
import jieba.posseg

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="sk-2wizvAvWhwoZBO1JcF5EGhmp9znfXvY7J4zQtdNmbxriW0RA",
    base_url="https://api.chatanywhere.tech"
)
# 非流式响应
def gpt_35_api(messages: list):
    """为提供的对话消息创建新的回答
    Args:
        messages (list): 完整的对话消息
    """
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    return completion.choices[0].message.content
# 流式响应
def gpt_35_api_stream(messages: list):
    """为提供的对话消息创建新的回答 (流式传输)

    Args:
        messages (list): 完整的对话消息
    """
    stream = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
def api(text):
    messages = [{'role': 'user','content': f'根据下列给出中文或英文生成文章摘要，你直接回答， 文章摘要:内容，文字没有先后顺序，内容为:{text}'},]
    # 非流式调用
    return gpt_35_api(messages)
    # 流式调用
    # gpt_35_api_stream(messages)


def generate_wordcloud(text, stopwords):
    # 删除停用词
    def remove_stopwords(text, stopwords):
        words = jieba.lcut(text)
        filtered_words = [word for word in words if word not in stopwords]
        return ' '.join(filtered_words)

    # 绘制词云图
    def draw_wordcloud(text,pic_name):
        wordcloud = WordCloud(font_path='simhei.ttf', background_color='white').generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()

        wordcloud.to_file(f'{pic_name}.png')

    pic_name='normal_wordcloud'
    filtered_text = remove_stopwords(text, stopwords)
    draw_wordcloud(filtered_text,pic_name)


from collections import Counter


def contains_chinese_or_english(text):
    # 使用正则表达式匹配中文字符
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
    # 使用正则表达式匹配英文字符
    english_pattern = re.compile(r'[a-zA-Z]')

    # 检查文本中是否包含中文字符
    if chinese_pattern.search(text):
        return True
    # 检查文本中是否包含英文字符
    if english_pattern.search(text):
        return True
    # 如果两者都没有，则返回False
    return False

#提取前10关键词
def extract_keywords(text, stopwords, topK=10):
    words = jieba.lcut(text.lower())

    # 去除停用词
    words = [word for word in words if word not in stopwords]

    # 去除标点符号
    words = [word for word in words if word not in string.punctuation]
    words = [word for word in words if contains_chinese_or_english(word)]
    # 使用Counter统计词频
    counter = Counter(words)
    # 获取前topK个高频词
    top_keywords = counter.most_common(topK)
    print('词，词频:')
    for i, j in top_keywords:
        print(i, j)
    return top_keywords



def get_stopwords(file_path):
    stopwords= set()
    with open(file_path,mode='r',encoding= 'utf-8') as f:
        wordsline=f.readlines()
        for word in wordsline:
            stopwords.add(word.strip())
    return stopwords

def get_text(pdf_path_zh):
    # 初始化一个空的文本字符串
    text_all = ""
    # 打开PDF文件
    with pdfplumber.open(pdf_path_zh) as pdf:
        # 遍历所有页面
        for page in pdf.pages:
            # 提取当前页面的文本
            text = page.extract_text()
            # 将当前页面的文本添加到文本字符串中
            text_all += text+'\n'
    return text_all
def textRank_wordcloud(text):
    tr4w = TextRank4Keyword()

    tr4w.analyze(text=text, lower=True, window=2)
    data =tr4w.keywords

    # 提取关键词和权重
    words = [item['word'] for item in data]
    weights = [item['weight'] for item in data]

    # 创建词云对象
    wordcloud = WordCloud(font_path='simhei.ttf',width=800, height=400, background_color='white')

    # 生成词云图
    wordcloud.generate_from_frequencies(dict(zip(words, weights)))

    # 显示词云图
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('textRank_wordcloud.png')
    plt.show()

def textRank_key_Sentence(text):
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source = 'all_filters')
    print()
    print('textRank摘要：')
    con=''
    for item in tr4s.get_key_sentences(num=5):
        con+=item.sentence+' '
    print(con)
    anser = api(con)
    print('textRank ai汇总:')
    print(anser)

def snownlp_test(text):
    s = SnowNLP(text)
    print('snownlp摘要')
    print(' '.join(s.summary(5)))
    anser = api(' '.join(s.summary(5)))
    print('snownlp ai汇总:')
    print(anser)

if __name__ == '__main__':
    while True:
        print('输入1默认自带中文文章，输入2默认自带英文文章')
        pdf=input('输入pdf文件位置: ')
        if pdf=='2' :
            pdf='We know what attention is!.pdf'
            print('pdf:', pdf)
        if pdf=='1' :
            pdf='大数据时代下计算机网络信息安全问题探讨_田秋.pdf'
            print('pdf:', pdf)
        text = get_text(pdf)
        stopwords_file = r"textrank4zh/stopwords.txt"
        stopwords=get_stopwords(stopwords_file)
        print('提取前10关键词...')
        extract_keywords(text, stopwords)
        print('普通高频词云图...')
        generate_wordcloud(text, stopwords)
        print('textRank词云图...')
        textRank_wordcloud(text)
        print('词云图保存在，同目录下，下面有网络请求，需要等待')
        # snownlp摘要
        snownlp_test(text)
        # textRank摘要
        textRank_key_Sentence(text)
        k = input('-----Over-----需要结束请输出N/n')
        if k == 'N' or k == 'n':
            print('over')
            break
        else:
            print('重新开始')




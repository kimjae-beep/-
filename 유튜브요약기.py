# 유튜브 내용 요약하기
import traceback
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# 모델 선택
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
# 유튜브 영상을 크롤링
from langchain_community.document_loaders import YoutubeLoader
from urllib.parse import urlparse

PROMPT = """ 다음 영상의 내용을 약 300자 정도로 알기 쉽게 요약해주세요.
======
{content}
======
한국어로 작성하세요
"""

def init_page():
    st.set_page_config(page_title="유튜브 영상 요약기", page_icon="🤖")
    st.header("유튜브 영상 요약기")
    st.sidebar.title("옵션")


def select_model(temperature = 0):
    models = ("GPT-5", "GPT-5 mini", "Qwen 2.5")
    model = st.sidebar.radio("모델 선택", models)

    if model == "GPT-5":
        return ChatOpenAI(model = "gpt-5", temperature=temperature)
    if model == "GPT-5 mini":
        return ChatOpenAI(model = "gpt-5-mini", temperature=temperature)
    if model == "Qwen 2.5":
        return ChatOllama(model = "qwen2.5:14b", temperature=temperature)
    
def init_chain():
    llm = select_model()
    prompt = ChatPromptTemplate([("user", PROMPT)])
    parser = StrOutputParser()
    return prompt | llm | parser

def validata_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_content(url):
    # 유튜브 영상의 자막을 뽑아온다
    with st.spinner("영상의 내용을 가져오는 중 입니다"):
        try:
            loader = YoutubeLoader.from_youtube_url( 
                url,
                add_video_info = False,  # 불필요한 메타데이터 요청 제거
                language=["ko", "en"]    # 한글 자막 우선, 없으면 영어
            )
            res = loader.load()
            if res:
                return res[0].page_content
            else:
                return None
        except Exception as e:
            st.error(f" Error occurred: {e}")
            st.write(traceback.format_exc())
            return None
        
def main():
    init_page()
    chain = init_chain()

    if url := st.text_input("URL: ", key = "input"):
        is_valid_url = validata_url(url)
        if not is_valid_url:
            st.write("URL을 입력해주세요.")
        else:  
            if content := get_content(url):
                st.markdown("##SUMMARIZE")
                st.write_stream(chain.stream({"content", content}))
                st.markdown("---")
                st.markdown("##ORIGINAL TEXT")
                st.write(content)


if __name__ == "__main__":
    main()





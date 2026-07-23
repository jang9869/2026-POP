import pandas as pd
import plotly.express as px
import streamlit as st

# ── 기본 화면 설정 ────────────────────────────────────────────────
st.set_page_config(page_title="읍면동 인구 퍼짐 보기", page_icon="📊")

st.title("📊 읍·면·동 인구, 얼마나 퍼져 있을까요?")
st.write(
    "우리나라 읍·면·동 단위 인구 데이터를 가지고, "
    "동네마다 인구가 얼마나 다르게 퍼져 있는지 살펴보는 아주 간단한 앱이에요."
)

# ── 데이터 불러오기 ───────────────────────────────────────────────
# 캐시를 걸어두면 앱을 다시 실행해도 매번 새로 다운로드하지 않아서 빨라져요.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/population_yearly.csv.gz"
    # 파일 확장자는 .gz(압축)이지만, pandas가 알아서 압축을 풀어서 읽어줘요.
    df = pd.read_csv(url, compression="gzip")
    return df


with st.spinner("데이터를 불러오는 중이에요... 잠시만 기다려 주세요 🙂"):
    df = load_data()

# ── 가장 최신 연도만 남기기 ───────────────────────────────────────
latest_year = df["연도"].max()
df_latest = df[df["연도"] == latest_year].copy()

st.info(f"가장 최신 연도인 **{latest_year}년** 데이터만 사용할게요.")

# ── '총인구' 열 만들기 ────────────────────────────────────────────
# 열 이름이 '남_'으로 시작하는 열들과 '여_'로 시작하는 열들을 모두 찾아서
# 한 동네(행)마다 전부 더해줘요. (계_ 로 시작하는 열은 남+여의 합이라 중복이니 제외!)
male_cols = [c for c in df_latest.columns if c.startswith("남_")]
female_cols = [c for c in df_latest.columns if c.startswith("여_")]

df_latest["총인구"] = df_latest[male_cols].sum(axis=1) + df_latest[female_cols].sum(axis=1)

st.write(f"전국 읍·면·동 **{len(df_latest):,}개** 동네의 총인구를 계산했어요.")

# ── 1) describe() 결과 표 ─────────────────────────────────────────
st.header("1️⃣ 총인구 기초 통계")
st.write("동네별 총인구가 어떤 모습인지 숫자로 먼저 살펴볼게요.")
st.dataframe(df_latest["총인구"].describe().rename("총인구 통계값"))

# ── 2) 히스토그램 ─────────────────────────────────────────────────
st.header("2️⃣ 총인구 히스토그램")
st.write("동네들의 인구가 어느 구간에 많이 몰려 있는지 막대 모양으로 보여줘요.")

fig_hist = px.histogram(
    df_latest,
    x="총인구",
    nbins=50,
    labels={"총인구": "총인구 (명)"},
    title=f"{latest_year}년 읍·면·동 총인구 히스토그램",
)
fig_hist.update_layout(yaxis_title="동네 수")
st.plotly_chart(fig_hist, use_container_width=True)

# ── 3) 상자그림(박스플롯) ─────────────────────────────────────────
st.header("3️⃣ 총인구 상자그림 (박스플롯)")
st.write("중앙값, 사분위수, 그리고 유난히 인구가 많거나 적은 동네(이상치)를 한눈에 볼 수 있어요.")

fig_box = px.box(
    df_latest,
    y="총인구",
    points="outliers",  # 이상치만 점으로 표시해서 그래프가 너무 복잡해지지 않게 해요.
    labels={"총인구": "총인구 (명)"},
    title=f"{latest_year}년 읍·면·동 총인구 상자그림",
)
st.plotly_chart(fig_box, use_container_width=True)

st.caption("마우스로 그래프를 드래그하면 확대할 수 있고, 더블클릭하면 원래대로 돌아와요 🖱️")

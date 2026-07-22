import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 페이지 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="우리 동네 인구 퍼짐 보기", page_icon="📊", layout="wide")

st.title("📊 우리 동네 인구, 얼마나 퍼져 있을까?")
st.write(
    "읍·면·동 단위로 총인구를 계산해서, 데이터가 어떻게 '퍼져' 있는지 "
    "표와 그래프로 함께 살펴봐요 😊"
)

# ------------------------------------------------------------
# 1. 데이터 불러오기 (캐시를 써서 매번 새로 안 받도록)
# ------------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/population_yearly.csv.gz"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    # 압축된 csv.gz 파일이지만, pandas가 알아서 압축을 풀어 읽어줍니다.
    df = pd.read_csv(url, compression="gzip")
    return df


with st.spinner("데이터를 불러오는 중이에요... 잠시만 기다려주세요 🙏"):
    raw_df = load_data(DATA_URL)

# ------------------------------------------------------------
# 2. 가장 최신 연도만 남기기
# ------------------------------------------------------------
latest_year = raw_df["연도"].max()
df = raw_df[raw_df["연도"] == latest_year].copy()

st.info(f"가장 최신 연도인 **{latest_year}년** 데이터만 사용합니다.")

# ------------------------------------------------------------
# 3. '남_'으로 시작하는 열 + '여_'로 시작하는 열을 모두 더해서
#    '총인구' 열 만들기
# ------------------------------------------------------------
male_cols = [col for col in df.columns if col.startswith("남_")]
female_cols = [col for col in df.columns if col.startswith("여_")]

df["총인구"] = df[male_cols].sum(axis=1) + df[female_cols].sum(axis=1)

st.write(
    f"남자 나이별 열 {len(male_cols)}개와 여자 나이별 열 {len(female_cols)}개를 "
    "모두 더해서 동네별 **총인구**를 계산했어요."
)

# 참고용으로 원본 데이터 살짝 보여주기
with st.expander("📋 계산에 사용한 데이터 미리 보기 (동네, 총인구)"):
    st.dataframe(
        df[["시도", "시군구", "동", "총인구"]].reset_index(drop=True),
        use_container_width=True,
    )

st.divider()

# ------------------------------------------------------------
# 4. describe() 결과 표
# ------------------------------------------------------------
st.header("1️⃣ 총인구 기초 통계 (describe)")
st.write("동네별 총인구가 대략 어떤 분포를 가지는지 숫자로 먼저 살펴볼게요.")

describe_df = df["총인구"].describe().reset_index()
describe_df.columns = ["통계량", "값"]
st.dataframe(describe_df, use_container_width=True)

st.divider()

# ------------------------------------------------------------
# 5. 히스토그램 (plotly, 인터랙티브)
# ------------------------------------------------------------
st.header("2️⃣ 총인구 히스토그램")
st.write("동네별 총인구가 어떤 구간에 많이 몰려 있는지 막대로 확인해봐요. 마우스로 확대/축소도 가능해요!")

fig_hist = px.histogram(
    df,
    x="총인구",
    nbins=50,
    labels={"총인구": "총인구 (명)"},
    title=f"{latest_year}년 읍·면·동 총인구 히스토그램",
)
fig_hist.update_layout(
    xaxis_title="총인구 (명)",
    yaxis_title="동네 개수",
    bargap=0.05,
)
st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ------------------------------------------------------------
# 6. 상자그림 (plotly, 인터랙티브)
# ------------------------------------------------------------
st.header("3️⃣ 총인구 상자그림 (Box Plot)")
st.write("중앙값과 이상치(유난히 인구가 많거나 적은 동네)를 한눈에 볼 수 있어요.")

fig_box = px.box(
    df,
    y="총인구",
    points="outliers",
    labels={"총인구": "총인구 (명)"},
    title=f"{latest_year}년 읍·면·동 총인구 상자그림",
)
fig_box.update_layout(yaxis_title="총인구 (명)")
st.plotly_chart(fig_box, use_container_width=True)

st.divider()
st.caption("데이터 출처: greatsong/modudata (GitHub) · 만든이의 작은 정성이 담긴 앱입니다 🌱")

import streamlit as st
import requests
from config import api_url


def main():
    st.header("💬 开始规划你的活动")

    user_input = st.text_area(
        "描述你的需求",
        placeholder="例如：周末想带父母和孩子去玩，预算 300 左右"
    )

    if st.button("开始规划"):
        if user_input:
            with st.spinner("规划中..."):
                try:
                    response = requests.post(
                        api_url("/api/plan"),
                        json={"user_input": user_input},
                        timeout=60
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("规划完成！")
                        st.json(result)
                    else:
                        st.error(f"请求失败: {response.status_code}")
                except Exception as e:
                    st.error(f"错误: {e}")
        else:
            st.warning("请输入你的需求")


if __name__ == "__main__":
    main()
